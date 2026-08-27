import pytest
import asyncio
from unittest.mock import patch

from app.agent import HRAgentOrchestrator
from app.storage.firestore_crypto import FirestoreStorageError
from app.storage.bigquery_audit import BigQueryAuditError

@pytest.mark.asyncio
async def test_vacation_balance_routing_trap_fixed():
    """Verify that vacation balance queries route strictly to WorkWeek HCM and NOT policy RAG."""
    orchestrator = HRAgentOrchestrator()
    
    # Query 1: Accrued and available vacation balances
    res1 = await orchestrator.run("What are my current accrued and available vacation balances?", employee_id="EMP-558")
    assert res1["status"] == "SUCCESS"
    assert "ww_get_employee_balances" in res1["tools_invoked"]
    assert "search_policy_handbook" not in res1["tools_invoked"]
    assert "Vacation" in res1["response"]

    # Query 2: Direct vacation balance check
    res2 = await orchestrator.run("Check my vacation balance", employee_id="EMP-558")
    assert res2["status"] == "SUCCESS"
    assert "ww_get_employee_balances" in res2["tools_invoked"]
    assert "search_policy_handbook" not in res2["tools_invoked"]

    # Query 3: Sick leave balance check
    res3 = await orchestrator.run("How many days of sick leave balance do I have left?", employee_id="EMP-558")
    assert res3["status"] == "SUCCESS"
    assert "ww_get_employee_balances" in res3["tools_invoked"]
    assert "search_policy_handbook" not in res3["tools_invoked"]

@pytest.mark.asyncio
async def test_database_write_error_not_silenced_firestore():
    """Verify that Firestore persistence failure returns DATABASE_ERROR status to client."""
    orchestrator = HRAgentOrchestrator()
    
    with patch.object(orchestrator.crypto_storage, "encrypt_transcript", side_effect=FirestoreStorageError("Simulated Firestore timeout write failure")):
        res = await orchestrator.run("What are my current accrued and available vacation balances?", employee_id="EMP-558")
        assert res["status"] == "DATABASE_ERROR"
        assert res["critic_verdict"] == "PERSISTENCE_FAILED"
        assert "Simulated Firestore timeout write failure" in res["error"]

@pytest.mark.asyncio
async def test_database_write_error_not_silenced_bigquery():
    """Verify that BigQuery audit logging failure returns DATABASE_ERROR status to client."""
    orchestrator = HRAgentOrchestrator()
    
    with patch.object(orchestrator.audit_logger, "log_audit_event", side_effect=BigQueryAuditError("Simulated BigQuery row insert quota error")):
        res = await orchestrator.run("What are my current accrued and available vacation balances?", employee_id="EMP-558")
        assert res["status"] == "DATABASE_ERROR"
        assert res["critic_verdict"] == "PERSISTENCE_FAILED"
        assert "Simulated BigQuery row insert quota error" in res["error"]
