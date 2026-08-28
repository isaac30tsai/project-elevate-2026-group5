"""Structured Pydantic Schemas for 4-Tier Benchmark Evaluation, Multi-LLM Judge & Intermediate Payloads."""
from typing import List, Optional, Dict, Any, Literal
import re
from pydantic import BaseModel, Field, field_validator

class SDPPayload(BaseModel):
    """Automated sensitive data protection schema validator for intermediate pipeline payloads."""
    phone: Optional[str] = None
    nric: Optional[str] = None
    account_number: Optional[str] = None
    
    @field_validator("phone", mode="before")
    def check_phone_masked(cls, v):
        if v and not any(m in v for m in ["[REDACTED_PHONE]", "[REDACTED]"]):
            if re.search(r"(?:\+65\s?)?[689][0-9]{3}[- ]?[0-9]{4}\b", str(v)):
                raise ValueError(f"Unmasked Singapore phone number detected in payload: {v}")
        return v

    @field_validator("nric", mode="before")
    def check_nric_masked(cls, v):
        if v and not any(m in v for m in ["[REDACTED_NRIC]", "[REDACTED]"]):
            if re.search(r"\b[STFGMstfgm][0-9]{7}[A-Za-z]\b", str(v)):
                raise ValueError(f"Unmasked Singapore NRIC/FIN detected in payload: {v}")
        return v

class FastMCPPayload(BaseModel):
    """Intermediate FastMCP SaaS payload validator enforcing type & domain boundaries."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    caller_id: str = "EMP-558"

    @field_validator("arguments")
    def check_tool_boundaries(cls, v):
        cat = v.get("category")
        if cat and cat not in ["Hardware", "Software", "Network", "HRSD", "Facilities", "Inquiry / Help"]:
            raise ValueError(f"Invalid ITSM category: {cat}")
        prio = v.get("priority")
        if prio and not any(p in str(prio) for p in ["1", "2", "3", "4"]):
            raise ValueError(f"Invalid ITSM priority: {prio}")
        l_type = v.get("leave_type")
        if l_type and l_type not in ["Vacation", "Sick"]:
            raise ValueError(f"Unsupported leave type for WorkWeek: {l_type}")
        return v

class LLMJudgeVerdict(BaseModel):
    """Structured verdict from Multi-LLM Consensus Judge with weighted scoring equations."""
    eval_id: str = Field(description="Test case identifier (e.g. EVAL-001)")
    ragas_groundedness: float = Field(default=1.0, ge=0.0, le=1.0, description="Factual adherence to retrieved context (0.0 - 1.0)")
    cosine_similarity: float = Field(default=1.0, ge=0.0, le=1.0, description="Semantic cosine similarity against ground truth claims")
    citation_accuracy: float = Field(default=1.0, ge=0.0, le=1.0, description="Presence and validity of handbook section citations (§)")
    context_hit_rate_at_k: float = Field(default=1.0, ge=0.0, le=1.0, description="Retrieval-stage context hit rate @ K=3 (0.0 - 1.0)")
    
    # Target Mathematical Score Formula (reference_approach.md Section 1.1):
    # formula: "0.30 * Groundedness + 0.20 * CosineSimilarity + 0.30 * CitationAccuracy + 0.20 * ContextHitRate"
    overall_run_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Weighted composite reliability score")
    
    zero_hallucination: bool = Field(default=True, description="True if 0% ungrounded claims detected")
    pii_leakage_detected: bool = Field(default=False, description="True if raw plaintext NRIC, phone, or financial PII leaked")
    policy_compliance: bool = Field(default=True, description="True if business rules and boundary constraints respected")
    reasoning: str = Field(default="Fully compliant with Altostrat Singapore policy guidelines.", description="Detailed explanation")
    verdict: Literal["PASSED", "FAILED", "BLOCKED"] = Field(default="PASSED", description="Final benchmark judgment")

    def compute_composite_score(self) -> float:
        self.overall_run_score = round(
            0.30 * self.ragas_groundedness +
            0.20 * self.cosine_similarity +
            0.30 * self.citation_accuracy +
            0.20 * self.context_hit_rate_at_k,
            4
        )
        return self.overall_run_score

class FinOpsTokenTracker(BaseModel):
    """FinOps token accounting and end-to-end lifecycle evaluation cost tracker."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    max_token_budget: int = 150_000
    estimated_cost_usd: float = 0.0
    
    # Human review & synthetic bootstrapping labor accounting
    human_review_labor_hours: float = 15.0
    human_hourly_rate_usd: float = 65.00
    synthetic_generation_tokens: int = 300_000
    synthetic_generation_cost_usd: float = 0.09000
    
    @property
    def total_human_labor_cost_usd(self) -> float:
        return self.human_review_labor_hours * self.human_hourly_rate_usd

    @property
    def total_lifecycle_cost_usd(self) -> float:
        return self.total_human_labor_cost_usd + self.synthetic_generation_cost_usd + self.estimated_cost_usd

    def add_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        # Pricing: Gemini 3.5 Flash $0.075 / 1M prompt, $0.30 / 1M completion
        self.estimated_cost_usd = (self.prompt_tokens * 0.075 / 1_000_000) + (self.completion_tokens * 0.30 / 1_000_000)

    def is_within_budget(self) -> bool:
        return self.total_tokens <= self.max_token_budget

class BusinessSLAMetrics(BaseModel):
    """Business SLA performance and latency benchmarks."""
    total_cases: int = 0
    passed_cases: int = 0
    latencies_ms: List[float] = Field(default_factory=list)
    p95_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    sla_target_p95_ms: float = 3000.0
    sla_compliance_rate: float = 0.0

    def compute_stats(self):
        if self.latencies_ms:
            sorted_lat = sorted(self.latencies_ms)
            self.avg_latency_ms = sum(sorted_lat) / len(sorted_lat)
            idx_95 = int(0.95 * len(sorted_lat))
            self.p95_latency_ms = sorted_lat[min(idx_95, len(sorted_lat) - 1)]
            compliant = sum(1 for l in self.latencies_ms if l <= self.sla_target_p95_ms)
            self.sla_compliance_rate = (compliant / len(self.latencies_ms)) * 100.0

class PlatformGuardrailScorecard(BaseModel):
    """Platform-native security and isolation scorecard."""
    model_armor_triggers: int = 0
    model_armor_total: int = 0
    identity_isolation_triggers: int = 0
    identity_isolation_total: int = 0
    pii_redaction_rate: float = 100.0  # Zero tolerance = 100% redacted
    dfa_state_machine_blocks: int = 0
    dfa_state_machine_total: int = 0
    intermediate_payload_checks_passed: int = 0
    intermediate_payload_checks_total: int = 0
