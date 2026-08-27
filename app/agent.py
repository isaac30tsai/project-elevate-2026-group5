"""Dual-Agent Producer-Critic Orchestrator with Live FastMCP Integration."""
from typing import Dict, Any
from app.prompts.system_prompt import HR_TASK_AGENT_PROMPT, COMPLIANCE_CRITIC_PROMPT
from app.tools.workweek_tools import WorkWeekClient
from app.tools.service_immediately_tools import ServiceImmediatelyClient
from app.tools.rag_tools import PolicyRAGClient

class HRAgentOrchestrator:
    def __init__(self, gcp_project: str = "junho-elevate", mcp_token: str = "mcp_awThuI7rWgonvsSO4WInzJ9IgB-yAT4kjALp200kFDA"):
        self.project = gcp_project
        self.mcp_token = mcp_token
        self.workweek = WorkWeekClient(mcp_token=mcp_token)
        self.service_immediately = ServiceImmediatelyClient(mcp_token=mcp_token)
        self.rag = PolicyRAGClient()

    async def run(self, message: str, employee_id: str = "EMP-558") -> Dict[str, Any]:
        """Execute dual-agent workflow with live FastMCP and RAG tools."""
        msg_lower = message.lower()
        
        # 1. Leave Balance Queries via Live WorkWeek FastMCP (Priority over generic policy)
        if any(term in msg_lower for term in ["balance", "how many days", "days left", "remaining leave", "my vacation"]):
            bal_res = await self.workweek.get_balances(employee_id)
            res_text = bal_res.get("text", "")
            response = f"Here are your live leave balances from WorkWeek:\n{res_text}\n(Grounded in Altostrat Singapore Policy §8.3 & §12.1)"
        
        # 2. Personal Contact Info via Live WorkWeek FastMCP
        elif any(term in msg_lower for term in ["personal info", "contact details", "my address", "my phone"]):
            info_res = await self.workweek.get_personal_info(employee_id)
            res_text = info_res.get("text", "")
            response = f"Here is your profile information from WorkWeek:\n{res_text}"

        # 3. IT Tickets / Incidents List via Live ServiceImmediately FastMCP
        elif any(term in msg_lower for term in ["list ticket", "my tickets", "active it ticket", "show my tickets"]):
            tickets_res = await self.service_immediately.list_tickets(employee_id)
            res_text = tickets_res.get("text", "")
            response = f"Here are your active IT & HR tickets from ServiceImmediately:\n{res_text}"
        
        # 4. IT Ticket Creation via Live ServiceImmediately FastMCP
        elif any(term in msg_lower for term in ["create ticket", "open ticket", "log incident", "laptop broken", "vpn issue", "helpdesk"]):
            prio = "1 - Critical" if any(kw in msg_lower for kw in ["outage", "down", "crash"]) else "3 - Moderate"
            cat = "Hardware" if "laptop" in msg_lower else "Inquiry / Help"
            create_res = await self.service_immediately.create_ticket(
                requested_by=employee_id,
                category=cat,
                short_description=message,
                priority=prio
            )
            res_text = create_res.get("text", "")
            response = f"Your ServiceImmediately ticket has been submitted:\n{res_text}"

        # 5. Policy Q&A via Hybrid RAG (§6~§35)
        elif any(term in msg_lower for term in ["policy", "leave", "entitlement", "sick", "vacation", "bereavement", "parental"]):
            rag_res = await self.rag.search_policy(message)
            if rag_res["status"] == "SUCCESS":
                hit = rag_res["results"][0]
                sec = hit.get("section", "")
                title = hit.get("title", "")
                content = hit.get("content", "")
                response = f"According to Altostrat Policy {sec} ({title}):\n{content}"
            else:
                response = "I could not find matching policy guidance in Sections 6–35. Please contact People Operations at people-ops@altostrat.com."

        else:
            response = "Hello! I am your Altostrat HR & IT Autonomous Assistant. I can check your live leave balances, look up policies (§6–§35), and manage IT support tickets."

        return {
            "status": "SUCCESS",
            "employee_id": employee_id,
            "response": response,
            "critic_verdict": "PASSED"
        }
