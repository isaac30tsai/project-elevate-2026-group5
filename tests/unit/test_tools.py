import pytest
import asyncio
from app.tools.workweek_tools import WorkWeekClient
from app.tools.service_immediately_tools import ServiceImmediatelyClient
from app.tools.rag_tools import PolicyRAGClient

@pytest.mark.asyncio
async def test_workweek_balances():
    client = WorkWeekClient()
    balances = await client.get_balances("EMP-4")
    assert balances["status"] == "SUCCESS"
    assert balances["vacation"]["available"] == 15.0
    assert balances["sick"]["available"] == 12.0

@pytest.mark.asyncio
async def test_service_immediately_create_ticket():
    client = ServiceImmediatelyClient()
    ticket = await client.create_incident("EMP-4", "Hardware", 3, "Laptop keyboard replacement")
    assert ticket["status"] == "CREATED"
    assert ticket["priority"] == 3
    assert ticket["current_status"] == "New"

@pytest.mark.asyncio
async def test_rag_policy_search():
    client = PolicyRAGClient()
    res = await client.search_policy("outpatient sick leave")
    assert res["status"] == "SUCCESS"
    assert len(res["results"]) > 0
    assert res["results"][0]["section"] == "§12.1"
