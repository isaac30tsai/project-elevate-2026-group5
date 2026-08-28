import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from app.agent import HRAgentOrchestrator
from app.tools.workweek_tools import WorkWeekClient
from app.tools.service_immediately_tools import ServiceImmediatelyClient

@pytest.mark.asyncio
async def test_d007_saga_successful_execution():
    """Verify that medical leave + delegation executes all 3 saga steps successfully."""
    orchestrator = HRAgentOrchestrator()
    query = "I need to take 3 days of medical leave starting next Monday and set up mailbox delegation"
    res = await orchestrator.run(query, employee_id="EMP-558")
    assert res["status"] == "SUCCESS"
    assert "ww_get_employee_balances" in res["tools_invoked"]
    assert "si_create_ticket" in res["tools_invoked"]
    assert "ww_request_time_off" in res["tools_invoked"]
    assert "si_rollback_ticket" not in res["tools_invoked"]

@pytest.mark.asyncio
async def test_d007_saga_automated_compensating_rollback():
    """Verify that when downstream leave request fails, D-007 automated rollback cancels the IT ticket."""
    orchestrator = HRAgentOrchestrator()
    query = "I need to take 3 days of medical leave starting next Monday and set up mailbox delegation"
    
    # Simulate failure on the 3rd step (WorkWeek leave request)
    with patch.object(orchestrator.workweek, "request_time_off", side_effect=RuntimeError("WorkWeek database connection dropped during commit")):
        with patch.object(orchestrator.service_immediately, "update_ticket_status", new_callable=AsyncMock) as mock_rollback:
            mock_rollback.return_value = {"status": "SUCCESS", "text": "Ticket INC123456 status updated to Canceled"}
            res = await orchestrator.run(query, employee_id="EMP-558")
            
            # Verify that rollback was executed
            assert "si_rollback_ticket" in res["tools_invoked"]
            assert mock_rollback.called
            call_args = mock_rollback.call_args[1]
            assert call_args["status"] == "Canceled"
            assert "Automated Saga Rollback (Design Decision D-007)" in call_args["resolution_notes"]

@pytest.mark.asyncio
async def test_rag_absent_policy_refusal():
    """Verify that policies not in handbook are answered with explicit HR referral notice and 0% hallucination."""
    orchestrator = HRAgentOrchestrator()
    query = "Does Altostrat reimburse pet insurance or veterinary bills?"
    res = await orchestrator.run(query, employee_id="EMP-558")
    assert res["status"] == "SUCCESS"
    # Must refuse with explicit policy referral notice
    assert "사내 정책 핸드북에 명시되지 않은 사항이므로 HR 담당자" in res["response"] or "not covered" in res["response"].lower() or "people-ops@altostrat.com" in res["response"]
    # Must not hallucinate coverage
    assert "reimbursed up to" not in res["response"].lower()
