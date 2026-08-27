"""BigQuery Compliance Lakehouse Audit Logger with Partitioned Table Inserts."""
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

class BigQueryAuditLogger:
    def __init__(self, dataset_id: Optional[str] = None):
        self.dataset_id = dataset_id or settings.bigquery_dataset
        self.table_id = "compliance_audit_log"
        self.bq_client = None
        if HAS_BQ_SDK:
            try:
                self.bq_client = bigquery.Client(project=settings.gcp_project)
            except Exception as e:
                logger.debug(f"BigQuery Client offline fallback: {e}")

    async def log_audit_event(
        self,
        employee_id: str,
        event_type: str,
        tool_name: str,
        compliance_verdict: str,
        trace_id: str
    ) -> Dict[str, Any]:
        """Record structured compliance audit row into BigQuery."""
        event_row = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "employee_role": "Engineering Staff",
            "event_type": event_type,
            "mcp_tool_name": tool_name,
            "compliance_verdict": compliance_verdict,
            "trace_id": trace_id
        }

        if self.bq_client:
            try:
                table_ref = f"{settings.gcp_project}.{self.dataset_id}.{self.table_id}"
                errors = self.bq_client.insert_rows_json(table_ref, [event_row])
                if errors:
                    logger.warning(f"BigQuery insert errors: {errors}")
            except Exception as e:
                logger.warning(f"BigQuery stream insert error: {e}")

        return event_row
