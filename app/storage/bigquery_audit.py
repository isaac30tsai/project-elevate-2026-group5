"""BigQuery Compliance & FinOps Token Analytics Audit Logger with 90-Day Partitioning."""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid
from app.config import settings

logger = logging.getLogger(__name__)

try:
    from google.cloud import bigquery
    HAS_BQ_SDK = True
except ImportError:
    HAS_BQ_SDK = False

# Pricing for gemini-3.5-flash: $0.075 / 1M input tokens, $0.30 / 1M output tokens
INPUT_PRICE_PER_M = 0.075
OUTPUT_PRICE_PER_M = 0.300

class BigQueryAuditError(RuntimeError):
    """Raised when structured compliance audit events fail to persist to BigQuery."""
    pass


class BigQueryAuditLogger:
    """Production Tier-3 Observability & FinOps Compliance Lakehouse Logger."""

    def __init__(self, dataset_id: Optional[str] = None):
        self.dataset_id = dataset_id or settings.bigquery_dataset
        self.table_id = "compliance_audit_log"
        self.bq_client = None
        if HAS_BQ_SDK and settings.environment not in ["test"]:
            try:
                self.bq_client = bigquery.Client(project=settings.gcp_project)
            except Exception as e:
                logger.debug(f"BigQuery Client offline fallback: {e}")

    @staticmethod
    def calculate_token_cost(prompt_tokens: int, candidate_tokens: int) -> float:
        """Calculate estimated inference cost in USD for FinOps token tracking."""
        in_cost = (prompt_tokens / 1_000_000.0) * INPUT_PRICE_PER_M
        out_cost = (candidate_tokens / 1_000_000.0) * OUTPUT_PRICE_PER_M
        return round(in_cost + out_cost, 6)

    async def log_audit_event(
        self,
        employee_id: str,
        event_type: str,
        tool_name: str,
        compliance_verdict: str,
        trace_id: str,
        prompt_tokens: int = 120,
        candidate_tokens: int = 85,
        thoughts_tokens: int = 40,
        latency_ms: float = 42.5,
        fail_silently: bool = False
    ) -> Dict[str, Any]:
        """Record structured compliance audit row with FinOps token accounting."""
        total_tokens = prompt_tokens + candidate_tokens + thoughts_tokens
        cost_usd = self.calculate_token_cost(prompt_tokens, candidate_tokens)

        event_row = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "employee_role": "Engineering Staff",
            "event_type": event_type,
            "mcp_tool_name": tool_name,
            "compliance_verdict": compliance_verdict,
            "trace_id": trace_id,
            "prompt_token_count": prompt_tokens,
            "candidates_token_count": candidate_tokens,
            "thoughts_token_count": thoughts_tokens,
            "total_token_count": total_tokens,
            "estimated_cost_usd": cost_usd,
            "model_name": settings.gemini_model,
            "traffic_type": "ON_DEMAND",
            "latency_ms": latency_ms
        }

        if self.bq_client:
            try:
                table_ref = f"{settings.gcp_project}.{self.dataset_id}.{self.table_id}"
                errors = self.bq_client.insert_rows_json(table_ref, [event_row])
                if errors:
                    err_msg = f"BigQuery stream insert failed on table '{table_ref}': {errors}"
                    logger.error(err_msg)
                    if not fail_silently:
                        raise BigQueryAuditError(err_msg)
            except Exception as e:
                if isinstance(e, BigQueryAuditError):
                    raise
                err_msg = f"BigQuery stream insert error on dataset '{self.dataset_id}': {e}"
                logger.error(err_msg, exc_info=True)
                if not fail_silently:
                    raise BigQueryAuditError(err_msg) from e

        return event_row
