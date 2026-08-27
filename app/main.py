"""Altostrat HR Agentic Solution - FastAPI REST Gateway & Gemini Enterprise Webhook App."""
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
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize agent orchestrator
agent = HRAgentOrchestrator(gcp_project=settings.gcp_project)

if HAS_FASTAPI:
    app = FastAPI(
        title="Altostrat HR Agentic Solution API",
        description="Production REST Gateway for Gemini Enterprise Front Door and Google Workspace Chat",
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
            "service": "altostrat-hr-agent",
            "model": settings.gemini_model,
            "project": settings.gcp_project
        }

    @app.post("/gemini-enterprise/chat")
    async def gemini_enterprise_webhook(request: Request):
        """Google Workspace Chat & Gemini Enterprise Webhook Endpoint."""
        headers = dict(request.headers)
        try:
            payload = await request.json()
        except Exception:
            payload = {}

        user_query = payload.get("message", {}).get("text", payload.get("text", ""))
        employee_id = GeminiEnterpriseAdapter.extract_user_identity(headers, payload)
        
        if not user_query:
            user_query = "Hello"

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
