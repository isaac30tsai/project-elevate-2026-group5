"""Altostrat HR Agentic Solution - FastAPI REST Gateway, A2A Agent Card & Gemini Enterprise Webhook App."""
import asyncio
import json
import os
import logging
from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, Request, HTTPException, status
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from app.agent import HRAgentOrchestrator
from app.gemini_enterprise_adapter import GeminiEnterpriseAdapter
from app.observability.telemetry import telemetry
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize agent orchestrator
agent = HRAgentOrchestrator(gcp_project=settings.gcp_project)

# Standard A2A Protocol Agent Card
A2A_AGENT_CARD = {
    "protocolVersion": "0.3.0",
    "name": "tpe-elevate-group5-agent",
    "description": "Altostrat Singapore HR & IT Autonomous Assistant powered by Gemini 3.5 Flash & Google ADK",
    "url": "https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app",
    "version": "1.0.0",
    "provider": {
        "organization": "Altostrat Singapore Technology",
        "url": "https://altostrat.com"
    },
    "capabilities": {
        "streaming": False,
        "humanInTheLoop": True
    },
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [
        {
            "id": "hr-policy-qa",
            "name": "HR Policy Q&A",
            "description": "Authoritative Singapore HR Handbook Policy Grounding (§6 to §35)",
            "tags": ["hr", "policy", "handbook", "singapore"]
        },
        {
            "id": "workweek-hcm",
            "name": "WorkWeek HCM Leave Management",
            "description": "Real-time leave balance inquiries and automated time off submission with -14d retroactivity check",
            "tags": ["leave", "vacation", "sick", "workweek"]
        },
        {
            "id": "service-immediately",
            "name": "ServiceImmediately ITSM Ticketing",
            "description": "IT Incident ticketing with automated P1-to-P4 priority guardrails",
            "tags": ["it", "incident", "ticket", "itsm"]
        }
    ]
}

if HAS_FASTAPI:
    app = FastAPI(
        title="Altostrat HR Agentic Solution API",
        description="Production REST Gateway, A2A Agent Card Registry, and Gemini Enterprise Front Door",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json"
    )

    @app.get("/")
    @app.get("/healthz")
    async def health_check():
        """Liveness & Readiness probe endpoint."""
        return {
            "status": "HEALTHY",
            "service": "tpe-elevate-group5-agent",
            "model": settings.gemini_model,
            "project": settings.gcp_project,
            "gemini_enterprise_status": "ENABLED"
        }

    @app.get("/.well-known/agent-card.json")
    @app.get("/a2a/app/.well-known/agent-card.json")
    async def get_agent_card():
        """Standard A2A Protocol Agent Card for Gemini Enterprise & Agent Registry discovery."""
        return A2A_AGENT_CARD

    @app.get("/v1/agent/registry")
    async def get_agent_registry():
        """Full Agent Registry Metadata (D-010 Specification)."""
        return {
            "registry_status": "REGISTERED",
            "agent_name": "tpe-elevate-group5-agent",
            "version": "1.0.0",
            "gemini_enterprise_engine": "projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486/assistants/default_assistant/agents/tpe-elevate-group5-agent",
            "backend_service_url": "https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app",
            "observability": {
                "tier1_cloud_trace": "ACTIVE",
                "tier2_pii_content_protection": "NO_CONTENT",
                "tier3_bigquery_finops": "ACTIVE",
                "tier4_otlp": "ENABLED"
            },
            "security": {
                "prompt_shield": "Google Cloud Model Armor (<50ms)",
                "envelope_encryption": "AES-256-GCM CMEK (Cloud KMS)",
                "identity_isolation": "Google IAP & OIDC JWT Claims (D-006)"
            },
            "card": A2A_AGENT_CARD
        }

    @app.post("/gemini-enterprise/chat")
    async def gemini_enterprise_webhook(request: Request):
        """Google Workspace Chat & Gemini Enterprise Webhook Endpoint."""
        with telemetry.span("gemini_enterprise_chat_request") as span_attrs:
            headers = dict(request.headers)
            try:
                payload = await request.json()
            except Exception:
                payload = {}

            user_query = payload.get("message", {}).get("text", payload.get("text", ""))
            employee_id = GeminiEnterpriseAdapter.extract_user_identity(headers, payload)
            
            if not user_query:
                user_query = "Hello"

            span_attrs["employee_id"] = employee_id
            span_attrs["user_query_len"] = len(user_query)

            agent_result = await agent.run(user_query, employee_id=employee_id)
            card_response = GeminiEnterpriseAdapter.build_chat_card_response(user_query, agent_result)
            return card_response

    @app.post("/v1/policy/search")
    async def search_policy_endpoint(payload: Dict[str, Any]):
        """REST Endpoint for searching Altostrat HR Policy Handbook (§6–§35)."""
        query = payload.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        res = await agent.rag.search_policy(query)
        return res

    @app.get("/v1/hcm/balances")
    async def get_hcm_balances_endpoint(employee_id: str = "EMP-558"):
        """REST Endpoint for retrieving WorkWeek HCM Leave Balances."""
        res = await agent.workweek.get_employee_balances(employee_id)
        return res

else:
    class AppFallback:
        def __call__(self, scope, receive, send):
            pass
    app = AppFallback()

async def main():
    print("=== Altostrat HR & IT Agentic Solution (MVP 1) ===")
    print(f"Target Model: {settings.gemini_model} | Project: {settings.gcp_project}")
    print("Simulating Gemini Enterprise Workspace Chat Inbound Message...")
    
    sample_headers = {
        "x-goog-authenticated-user-email": "accounts.google.com:junhojang@altostrat.com"
    }
    sample_chat_payload = {
        "type": "MESSAGE",
        "message": {
            "text": "How many days of vacation and sick leave do I have remaining?"
        },
        "user": {
            "email": "junhojang@altostrat.com",
            "displayName": "Junho Jang"
        }
    }
    
    employee_id = GeminiEnterpriseAdapter.extract_user_identity(sample_headers, sample_chat_payload)
    res = await agent.run(sample_chat_payload["message"]["text"], employee_id=employee_id)
    card_out = GeminiEnterpriseAdapter.build_chat_card_response(sample_chat_payload["message"]["text"], res)
    print("[Gemini Enterprise CardV2 Output]:")
    print(json.dumps(card_out, indent=2))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    if HAS_FASTAPI:
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        asyncio.run(main())
