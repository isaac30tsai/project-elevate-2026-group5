import pytest
from app.agent import HRAgentOrchestrator

@pytest.mark.asyncio
async def test_agent_policy_qa_grounding():
    orchestrator = HRAgentOrchestrator(gcp_project="junho-elevate")
    res = await orchestrator.run("What is the policy on bereavement leave?", employee_id="EMP-4")
    assert res["status"] == "SUCCESS"
    assert "§14.2" in res["response"]
    assert res["critic_verdict"] == "PASSED"

@pytest.mark.asyncio
async def test_agent_leave_balance_lookup():
    orchestrator = HRAgentOrchestrator(gcp_project="junho-elevate")
    res = await orchestrator.run("How many days of vacation balance do I have left?", employee_id="EMP-4")
    assert res["status"] == "SUCCESS"
    assert "15.0 days available" in res["response"]
