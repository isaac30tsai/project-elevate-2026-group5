import pytest
from app.tools.service_immediately_tools import ServiceImmediatelyClient
from app.tools.workweek_tools import WorkWeekClient

@pytest.mark.asyncio
async def test_priority_downgrade_without_critical_keyword():
    client = ServiceImmediatelyClient()
    ticket = await client.create_incident("EMP-4", "Software", 1, "Please install python")
    assert ticket["priority"] == 4, "Priority 1 without critical keywords must be downgraded to 4"

@pytest.mark.asyncio
async def test_unsupported_leave_type_rejection():
    client = WorkWeekClient()
    res = await client.request_time_off("EMP-4", "Maternity", "2026-09-01", "2026-12-01", 60.0)
    assert res["status"] == "ERROR"
    assert res["code"] == "UNSUPPORTED_LEAVE_TYPE"
