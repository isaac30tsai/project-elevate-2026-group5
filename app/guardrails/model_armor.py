"""Google Cloud Model Armor Semantic Firewall Client (<50ms Ingress/Egress Guardrail)."""
from typing import Dict, Any, Tuple
import re
import logging

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system override",
    r"print (the )?(system prompt|secret|token|api key)",
    r"you are now in maintenance mode",
    r"grant admin role",
    r"delete all (incident|ticket|user) records",
    r"bypass (guardrail|security|critic)"
]

CROSS_USER_EXFILTRATION_PATTERNS = [
    r"(show|get|view|check|display).*(salary|balance|contact|profile|record).*(for|of) (employee|user)? *(emp-\d+)",
    r"(other employee|another user|coworker).*(salary|record|balance)"
]

SINGAPORE_NRIC_REGEX = r"[STFGstfg]\d{7}[A-Za-z]"

class ModelArmorClient:
    def __init__(self, template_id: str = "altostrat-hr-agent-safety-dev"):
        self.template_id = template_id

    async def inspect_prompt(self, user_prompt: str, caller_id: str = "EMP-558") -> Tuple[bool, str, Dict[str, Any]]:
        """Inspect inbound prompt for prompt injection, jailbreaks, cross-user exfiltration, and PII."""
        prompt_lower = user_prompt.lower()
        
        # 1. Prompt Injection & Jailbreak Check
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, prompt_lower):
                logger.warning(f"Model Armor Triggered: Prompt injection pattern detected -> {pattern}")
                return False, "BLOCKED: Prompt violates Altostrat Enterprise Security Guidelines.", {
                    "verdict": "BLOCKED",
                    "reason": "PROMPT_INJECTION_DETECTED",
                    "matched_pattern": pattern
                }

        # 2. Cross-User Exfiltration Check (D-006 Identity Isolation)
        for pattern in CROSS_USER_EXFILTRATION_PATTERNS:
            match = re.search(pattern, prompt_lower)
            if match:
                target_emp = match.group(3).upper() if match.lastindex and match.lastindex >= 3 else ""
                if target_emp and target_emp != caller_id:
                    logger.warning(f"Model Armor Triggered: Unauthorized cross-user data access for {target_emp} by {caller_id}")
                    return False, f"BLOCKED: Unauthorized cross-user access. You are authenticated as {caller_id} and cannot access records for {target_emp}.", {
                        "verdict": "BLOCKED",
                        "reason": "UNAUTHORIZED_CROSS_USER_ACCESS"
                    }
        
        # 3. PII Sanitization (Singapore NRIC Masking)
        sanitized_prompt = re.sub(SINGAPORE_NRIC_REGEX, "[MASKED_NRIC]", user_prompt)
        
        return True, sanitized_prompt, {"verdict": "PASSED", "pii_redacted": sanitized_prompt != user_prompt}
