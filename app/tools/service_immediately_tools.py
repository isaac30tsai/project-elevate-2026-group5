"""ServiceImmediately ITSM Live FastMCP Tool Client."""
from typing import Dict, Any
import urllib.request, json

SI_MCP_URL = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"
DEFAULT_TOKEN = "mcp_awThuI7rWgonvsSO4WInzJ9IgB-yAT4kjALp200kFDA"

class ServiceImmediatelyClient:
    def __init__(self, mcp_token: str = DEFAULT_TOKEN):
        self.url = SI_MCP_URL
        self.token = mcp_token
        self.headers = {
            "Authorization": f"Bearer {mcp_token}",
            "X-MCP-Token": mcp_token,
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

    def _call_mcp(self, tool_name: str, arguments: Dict[str, Any], call_id: int = 1) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
            "id": call_id
        }
        try:
            req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=self.headers, method="POST")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_out = data.get("result", {}).get("content", [{}])[0].get("text", "")
                return {"status": "SUCCESS", "raw": data, "text": text_out}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    async def list_tickets(self, employee_id: str = "EMP-558") -> Dict[str, Any]:
        return self._call_mcp("list_tickets", {"employee_id": employee_id})

    async def create_ticket(self, requested_by: str, category: str, short_description: str, priority: str = "3 - Moderate") -> Dict[str, Any]:
        # Guardrail: auto-downgrade priority 1 without critical keywords
        critical_kws = ["outage", "crash", "down", "offline", "unresponsive"]
        if "1" in priority and not any(kw in short_description.lower() for kw in critical_kws):
            priority = "4 - Low"

        return self._call_mcp("create_ticket", {
            "requested_by": requested_by,
            "category": category,
            "short_description": short_description,
            "priority": priority
        })

    async def update_ticket_status(self, ticket_id: str, status: str, resolution_notes: str = "") -> Dict[str, Any]:
        return self._call_mcp("update_ticket_status", {
            "ticket_id": ticket_id,
            "status": status,
            "resolution_notes": resolution_notes
        })
