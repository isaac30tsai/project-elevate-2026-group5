"""Centralized Configuration Management with Environment Variable Externalization."""
import os
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Settings:
    # GCP Environment
    gcp_project: str = os.getenv("GCP_PROJECT", "junho-elevate")
    region: str = os.getenv("GCP_REGION", "asia-southeast1")
    environment: str = os.getenv("ENVIRONMENT", "dev")
    
    # Model Configurations
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    
    # SaaS FastMCP Endpoints (Externalized)
    workweek_base_url: str = os.getenv(
        "WORKWEEK_BASE_URL",
        "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/"
    )
    service_immediately_base_url: str = os.getenv(
        "SERVICE_IMMEDIATELY_BASE_URL",
        "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"
    )
    # Strictly read from environment / Secret Manager (Zero hardcoded secrets)
    mcp_auth_token: str = os.getenv("MCP_AUTH_TOKEN", "")
    
    # Knowledge & RAG
    datastore_id: str = os.getenv("DATASTORE_ID", "altostrat-hr-policy-datastore-dev")
    
    # Security & Storage
    kms_key_id: Optional[str] = os.getenv("KMS_KEY_ID", None)
    firestore_db: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "altostrat_hr_analytics")

settings = Settings()
