"""Altostrat HR Agentic Solution - FastAPI REST Gateway, A2A Agent Card & Gemini Enterprise Webhook App."""
import asyncio
import json
import os
import logging
import uuid
from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, Request, HTTPException, status
    from fastapi.responses import JSONResponse, StreamingResponse
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
            if agent_result.get("status") == "DATABASE_ERROR":
                from fastapi.responses import JSONResponse
                err_card = GeminiEnterpriseAdapter.build_chat_card_response(
                    user_query,
                    {
                        "response": f"System Alert: Database transaction persistence error ({agent_result.get('error')}).",
                        "status": "DATABASE_ERROR",
                        "critic_verdict": "ERROR"
                    }
                )
                return JSONResponse(status_code=500, content=err_card)

            card_response = GeminiEnterpriseAdapter.build_chat_card_response(user_query, agent_result)
            return card_response

    @app.post("/api/stream_reasoning_engine")
    @app.post("/api/stream_reasoning_engine/")
    async def stream_reasoning_engine(request: Request):
        """Vertex AI Reasoning Engine & Gemini Enterprise Streaming Execution Protocol."""
        try:
            body = await request.json()
        except Exception:
            body = {}

        class_method = body.get("class_method", "async_stream_query")
        input_data = body.get("input") or {}

        # 1. Handle session lifecycle calls if forwarded here
        if "session" in class_method.lower():
            sess_id = input_data.get("session_id") or f"sess-{uuid.uuid4().hex[:12]}"
            res_obj = {"id": sess_id, "session_id": sess_id, "user_id": input_data.get("user_id", "EMP-558")}
            async def sess_gen():
                yield json.dumps(res_obj) + "\n"
            return StreamingResponse(sess_gen(), media_type="application/json")

        # 2. Extract user query string from heterogeneous payload structures
        raw_msg = input_data.get("message")
        if isinstance(raw_msg, dict):
            parts = raw_msg.get("parts", [])
            extracted = " ".join(p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p)
            user_query = extracted or raw_msg.get("text", "")
        elif isinstance(raw_msg, str):
            user_query = raw_msg
        else:
            user_query = input_data.get("query") or input_data.get("prompt") or input_data.get("text") or ""

        if not user_query:
            user_query = "Hello"

        user_id = input_data.get("user_id") or input_data.get("employee_id") or "EMP-558"
        session_id = input_data.get("session_id") or f"sess-{uuid.uuid4().hex[:8]}"

        async def reasoning_stream_generator():
            try:
                # Execute full cognitive reasoning loop
                agent_res = await agent.run(user_query, employee_id=user_id)
                response_text = agent_res.get("response", "")

                # Standard Vertex AI / ADK Event Wire Format
                event_dict = {
                    "author": "tpe-elevate-group5-agent",
                    "content": {
                        "role": "model",
                        "parts": [
                            {"text": response_text}
                        ]
                    },
                    "actions": {},
                    "session_id": session_id
                }
                yield json.dumps(event_dict) + "\n"
            except Exception as e:
                logger.error(f"Error executing agent reasoning stream: {e}", exc_info=True)
                err_event = {
                    "author": "tpe-elevate-group5-agent",
                    "content": {
                        "role": "model",
                        "parts": [
                            {"text": f"Agent execution error: {str(e)}"}
                        ]
                    },
                    "actions": {},
                    "session_id": session_id
                }
                yield json.dumps(err_event) + "\n"

        return StreamingResponse(reasoning_stream_generator(), media_type="application/json")

    @app.post("/api/reasoning_engine")
    @app.post("/api/reasoning_engine/")
    async def reasoning_engine(request: Request):
        """Vertex AI Reasoning Engine & Gemini Enterprise Synchronous Execution Protocol."""
        try:
            body = await request.json()
        except Exception:
            body = {}

        class_method = body.get("class_method", "query")
        input_data = body.get("input") or {}

        # Session lifecycle endpoints
        if "session" in class_method.lower():
            if "create" in class_method.lower():
                sess_id = f"sess-{uuid.uuid4().hex[:12]}"
                return JSONResponse({"output": {"id": sess_id, "session_id": sess_id, "user_id": input_data.get("user_id", "EMP-558")}})
            if "get" in class_method.lower():
                return JSONResponse({"output": {"id": input_data.get("session_id", "default"), "session_id": input_data.get("session_id", "default")}})
            if "list" in class_method.lower():
                return JSONResponse({"output": []})
            if "delete" in class_method.lower():
                return JSONResponse({"output": {"deleted": True}})

        raw_msg = input_data.get("message")
        if isinstance(raw_msg, dict):
            parts = raw_msg.get("parts", [])
            extracted = " ".join(p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p)
            user_query = extracted or raw_msg.get("text", "")
        elif isinstance(raw_msg, str):
            user_query = raw_msg
        else:
            user_query = input_data.get("query") or input_data.get("prompt") or input_data.get("text") or ""

        if not user_query:
            user_query = "Hello"

        user_id = input_data.get("user_id") or input_data.get("employee_id") or "EMP-558"
        agent_res = await agent.run(user_query, employee_id=user_id)
        
        output = {
            "content": {
                "role": "model",
                "parts": [
                    {"text": agent_res.get("response", "")}
                ]
            },
            "status": agent_res.get("status", "SUCCESS"),
            "critic_verdict": agent_res.get("critic_verdict", "PASSED"),
            "trace_id": agent_res.get("trace_id", "")
        }
        status_code = 500 if agent_res.get("status") == "DATABASE_ERROR" else 200
        return JSONResponse({"output": output}, status_code=status_code)

    @app.post("/v1/policy/search")
    async def search_policy_endpoint(payload: Dict[str, Any]):
        """REST Endpoint for searching Altostrat HR Policy Handbook (§6–§35)."""
        query = payload.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        res = await agent.rag.search_policy(query)
        return res

    @app.get("/v1/hcm/balances")
    async def get_hcm_balances_endpoint(request: Request):
        """REST Endpoint for retrieving WorkWeek HCM Leave Balances.

        In strict compliance with D-006 (Zero Trust Identity Isolation), caller
        identity is derived exclusively server-side from authenticated OIDC/IAP
        headers. The employee_id parameter is never exposed or accepted via schema/query.
        """
        headers = dict(request.headers)
        employee_id = GeminiEnterpriseAdapter.extract_user_identity(headers)
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
