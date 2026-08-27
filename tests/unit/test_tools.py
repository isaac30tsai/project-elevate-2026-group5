"""Unit tests for WorkWeek, ServiceImmediately, and Policy RAG tools."""
import pytest
from app.tools.workweek_tools import WorkWeekClient
from app.tools.service_immediately_tools import ServiceImmediatelyClient
from app.tools.rag_tools import PolicyRAGClient

@pytest.mark.asyncio
async def test_workweek_balances():
    client = WorkWeekClient()
    balances = await client.get_employee_balances("EMP-558")
    assert balances["status"] == "SUCCESS"
    assert "Vacation" in balances["text"]

@pytest.mark.asyncio
async def test_service_immediately_create_ticket():
    client = ServiceImmediatelyClient()
    ticket = await client.create_ticket("EMP-558", "Hardware", "Laptop keyboard replacement", "3 - Moderate")
    assert ticket["status"] == "SUCCESS"

@pytest.mark.asyncio
async def test_rag_policy_search():
    client = PolicyRAGClient()
    res = await client.search_policy("outpatient sick leave")
    assert res["status"] == "SUCCESS"
    assert len(res["results"]) > 0
    assert "§12.1" in res["primary_section"]
