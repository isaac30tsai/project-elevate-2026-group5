"""WorkWeek HCM Live FastMCP Tool Client."""
from typing import Dict, Any
import urllib.request, json

WORKWEEK_MCP_URL = "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/"
DEFAULT_TOKEN = "mcp_awThuI7rWgonvsSO4WInzJ9IgB-yAT4kjALp200kFDA"

class WorkWeekClient:
    def __init__(self, mcp_token: str = DEFAULT_TOKEN):
        self.url = WORKWEEK_MCP_URL
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

    async def get_current_employee_id(self) -> str:
        res = self._call_mcp("get_current_employee_id", {})
        return res.get("text", "EMP-558")

    async def get_balances(self, employee_id: str = "EMP-558") -> Dict[str, Any]:
        res = self._call_mcp("get_employee_balances", {"employee_id": employee_id})
        return res

    async def get_personal_info(self, employee_id: str = "EMP-558") -> Dict[str, Any]:
        res = self._call_mcp("get_personal_info", {"employee_id": employee_id})
        return res

    async def request_time_off(self, employee_id: str, leave_type: str, start_date: str, end_date: str, days: float) -> Dict[str, Any]:
        res = self._call_mcp("request_time_off", {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        })
        return res
