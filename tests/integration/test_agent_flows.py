import pytest
from app.agent import HRAgentOrchestrator

@pytest.mark.asyncio
async def test_agent_policy_qa():
    orchestrator = HRAgentOrchestrator()
    res = await orchestrator.run("What is the bereavement leave policy for immediate family members?", employee_id="EMP-558")
    assert res["status"] == "SUCCESS"
    assert "§14.2" in res["response"]
    assert res["critic_verdict"] == "PASSED"

@pytest.mark.asyncio
async def test_agent_leave_balance():
    orchestrator = HRAgentOrchestrator()
    res = await orchestrator.run("What are my current accrued and available vacation balances?", employee_id="EMP-558")
    assert res["status"] == "SUCCESS"
    assert "Vacation" in res["response"]
