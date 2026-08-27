"""Altostrat HR Agentic Solution - Main Entrypoint & Gemini Enterprise Webhook Gateway."""
import asyncio
import json
from typing import Dict, Any
from app.agent import HRAgentOrchestrator
from app.gemini_enterprise_adapter import GeminiEnterpriseAdapter

agent = HRAgentOrchestrator(gcp_project="junho-elevate")

async def handle_gemini_enterprise_webhook(headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process incoming events from Google Workspace Chat & Gemini Enterprise."""
    user_query = payload.get("message", {}).get("text", payload.get("text", ""))
    
    # Extract identity
    employee_id = GeminiEnterpriseAdapter.extract_user_identity(headers, payload)
    
    if not user_query:
        user_query = "Hello"

    # Execute dual-agent workflow
    agent_result = await agent.run(user_query, employee_id=employee_id)
    
    # Format CardV2 response for Gemini Enterprise
    card_response = GeminiEnterpriseAdapter.build_chat_card_response(user_query, agent_result)
    return card_response

async def main():
    print("=== Altostrat HR & IT Agentic Solution (MVP 1) ===")
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
    
    card_out = await handle_gemini_enterprise_webhook(sample_headers, sample_chat_payload)
    print("\n[Gemini Enterprise CardV2 Output]:")
    print(json.dumps(card_out, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
