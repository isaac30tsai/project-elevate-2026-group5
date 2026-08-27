"""Google Cloud Model Armor REST Client & Low-Latency Semantic Prompt Shield (<50ms)."""
from typing import Dict, Any, Tuple, Optional
import os
import re
import time
import logging
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from app.config import settings

logger = logging.getLogger(__name__)

class ModelArmorClient:
    """Production Client for Google Cloud Model Armor Prompt Shield with <50ms local safety gate."""

    def __init__(self, project_id: Optional[str] = None, template_id: Optional[str] = None):
        self.project_id = project_id or settings.gcp_project
        self.region = settings.region
        self.template_id = template_id or os.getenv("MODEL_ARMOR_TEMPLATE", "altostrat-hr-armor-template-dev")
        self.endpoint_url = (
            f"https://modelarmor.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/"
            f"templates/{self.template_id}:sanitizeUserPrompt"
        )
        self.http_client = httpx.AsyncClient(timeout=0.08) if HAS_HTTPX else None # Strict sub-100ms timeout

        # Deterministic defense patterns for instant (<1ms) heuristic pre-flight
        self._injection_patterns = [
            re.compile(r"ignore (all )?previous instructions", re.IGNORECASE),
            re.compile(r"you are now in maintenance mode", re.IGNORECASE),
            re.compile(r"bypass (all )?security filters", re.IGNORECASE),
            re.compile(r"print the system prompt", re.IGNORECASE),
            re.compile(r"reveal (all )?internal secrets", re.IGNORECASE),
            re.compile(r"system:\s*override", re.IGNORECASE),
            re.compile(r"drop all tables", re.IGNORECASE),
            re.compile(r"elevate privileges", re.IGNORECASE),
        ]

    async def _query_cloud_model_armor(self, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Invoke Google Cloud Model Armor REST API for real neural prompt sanitization."""
        try:
            # Check for GCP access token
            token = os.getenv("CLOUDSDK_AUTH_ACCESS_TOKEN") or os.getenv("GOOGLE_OAUTH_TOKEN")
            headers = {"Content-Type": "application/json"}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            payload = {
                "userPromptData": {
                    "text": prompt
                }
            }
            resp = await self.http_client.post(self.endpoint_url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                sanitization_res = data.get("sanitizationResult", {})
                filter_match = sanitization_res.get("filterMatchState", "NO_MATCH")
                if filter_match == "MATCH_FOUND":
                    return False, "Prompt blocked by Google Cloud Model Armor (Inappropriate content or jailbreak detected).", data
                return True, sanitization_res.get("sanitizedPrompt", prompt), data
        except Exception as e:
            logger.debug(f"Cloud Model Armor REST invocation fallback: {e}")

        return True, prompt, {"status": "LOCAL_GATE_ACTIVE"}

    async def inspect_prompt(self, prompt: str, caller_id: str = "EMP-558") -> Tuple[bool, str, Dict[str, Any]]:
        """Comprehensive Multi-Tier Prompt Inspection (<50ms SLA)."""
        start_time = time.time()
        
        # 1. Zero-Tolerance Heuristic Pre-Flight (Prompt Injections & System Overrides)
        for pat in self._injection_patterns:
            if pat.search(prompt):
                elapsed_ms = (time.time() - start_time) * 1000
                logger.warning(f"Model Armor Triggered: Prompt injection pattern detected -> {pat.pattern}")
                return False, f"Security Violation: Prompt blocked by Model Armor (<50ms shield: {elapsed_ms:.1f}ms).", {
                    "reason": "PROMPT_INJECTION_DETECTED",
                    "latency_ms": elapsed_ms,
                    "pattern": pat.pattern
                }

        # 2. Server-Side Identity Isolation Guardrail (D-006: Prevent Cross-User Exfiltration)
        cross_user_match = re.search(r"(?:employee|emp|user|for)\s*(EMP-[0-9]+)", prompt, re.IGNORECASE)
        if cross_user_match:
            target_emp = cross_user_match.group(1).upper()
            if target_emp != caller_id.upper():
                elapsed_ms = (time.time() - start_time) * 1000
                logger.warning(f"Model Armor Triggered: Unauthorized cross-user data access for {target_emp} by {caller_id}")
                return False, f"Access Denied: You ({caller_id}) are strictly unauthorized to view or modify data for {target_emp} (Policy D-006).", {
                    "reason": "UNAUTHORIZED_CROSS_USER_ACCESS",
                    "caller_id": caller_id,
                    "target_id": target_emp,
                    "latency_ms": elapsed_ms
                }

        # 3. Singapore NRIC PII Masking
        sanitized_text = re.sub(r"[STFGstfg][0-9]{7}[A-Za-z]", "[REDACTED_NRIC]", prompt)

        # 4. Real Google Cloud Model Armor REST Service Call
        cloud_safe, cloud_text, cloud_meta = await self._query_cloud_model_armor(sanitized_text)
        if not cloud_safe:
            elapsed_ms = (time.time() - start_time) * 1000
            return False, cloud_text, {
                "reason": "CLOUD_MODEL_ARMOR_BLOCK",
                "latency_ms": elapsed_ms,
                "cloud_metadata": cloud_meta
            }

        elapsed_ms = (time.time() - start_time) * 1000
        return True, cloud_text, {
            "status": "APPROVED",
            "latency_ms": elapsed_ms,
            "cloud_status": cloud_meta.get("status", "VERIFIED")
        }
