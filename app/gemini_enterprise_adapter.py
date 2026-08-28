"""Gemini Enterprise & Google Workspace Chat Adapter with Interactive CardV2 Rendering."""
from typing import Dict, Any, Optional
import json

class GeminiEnterpriseAdapter:
    """Transforms incoming Gemini Enterprise / Google Chat events and renders CardV2 responses."""

    @staticmethod
    def extract_user_identity(headers: Dict[str, str], payload: Dict[str, Any]) -> str:
        """Extract authenticated caller identity from Google Cloud Identity / OIDC headers."""
        # 1. Check IAP / Cloud Identity header
        auth_email = headers.get("x-goog-authenticated-user-email", "")
        if auth_email:
            email_clean = auth_email.replace("accounts.google.com:", "")
            # Mapping demo email to employee ID
            if any(k in email_clean.lower() for k in ["employee", "demo", "altostrat", "emp-558"]):
                return "EMP-558"
        
        # 2. Check Google Chat event sender
        sender_email = payload.get("user", {}).get("email", "")
        if any(k in sender_email.lower() for k in ["employee", "demo", "altostrat", "emp-558"]):
            return "EMP-558"
            
        return payload.get("employee_id", "EMP-558")

    @staticmethod
    def build_chat_card_response(query: str, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build rich Google Chat CardV2 widget for Gemini Enterprise / Workspace Chat."""
        response_text = agent_result.get("response", "")
        emp_id = agent_result.get("employee_id", "EMP-558")
        verdict = agent_result.get("critic_verdict", "PASSED")

        card_v2 = {
            "cardsV2": [
                {
                    "cardId": "altostrat-hr-response-card",
                    "card": {
                        "header": {
                            "title": "Altostrat HR & IT Autonomous Assistant",
                            "subtitle": f"Caller: {emp_id} | Compliance Check: {verdict}",
                            "imageUrl": "https://fonts.gstatic.com/s/i/short-term/release/googlegsymbol/robot_2/default/24px.svg",
                            "imageType": "CIRCLE"
                        },
                        "sections": [
                            {
                                "header": "Inquiry Details",
                                "widgets": [
                                    {
                                        "decoratedText": {
                                            "topLabel": "User Inquiry",
                                            "text": query,
                                            "wrapText": True
                                        }
                                    },
                                    {
                                        "divider": {}
                                    },
                                    {
                                        "decoratedText": {
                                            "topLabel": "Agent Resolution (Grounded in §6–§35 & Live SaaS)",
                                            "text": response_text.replace("\n", "<br>"),
                                            "wrapText": True
                                        }
                                    }
                                ]
                            },
                            {
                                "widgets": [
                                    {
                                        "buttonList": {
                                            "buttons": [
                                                {
                                                    "text": "View Policy Handbook",
                                                    "onClick": {
                                                        "openLink": {
                                                            "url": "https://docs.google.com/document/d/1omb7qXPLlY6H5PSH-dTra8pYwDX9fWG2NLqUdHFPZ3M/edit?usp=sharing&resourcekey=0-FRWtPHULk0dwogTNAEgNfw"
                                                        }
                                                    }
                                                },
                                                {
                                                    "text": "WorkWeek HCM",
                                                    "onClick": {
                                                        "openLink": {
                                                            "url": "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/"
                                                        }
                                                    }
                                                },
                                                {
                                                    "text": "ServiceImmediately ITSM",
                                                    "onClick": {
                                                        "openLink": {
                                                            "url": "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/"
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        return card_v2
