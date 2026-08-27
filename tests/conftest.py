import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_gcp_clients_for_tests(monkeypatch):
    """Prevent hanging or auth failures on expired local ADC credentials during test runs."""
    mock_kms = MagicMock()
    mock_kms.encrypt.side_effect = lambda request: MagicMock(ciphertext=b"mock-kms-wrapped-" + request["plaintext"])
    mock_kms.decrypt.side_effect = lambda request: MagicMock(plaintext=request["ciphertext"].replace(b"mock-kms-wrapped-", b""))

    mock_firestore = MagicMock()
    
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = []  # No insertion errors
    
    try:
        from google.cloud import kms_v1, firestore, bigquery
        monkeypatch.setattr(kms_v1, "KeyManagementServiceClient", lambda *args, **kwargs: mock_kms)
        monkeypatch.setattr(firestore, "Client", lambda *args, **kwargs: mock_firestore)
        monkeypatch.setattr(bigquery, "Client", lambda *args, **kwargs: mock_bq)
    except ImportError:
        pass

    try:
        from google import genai
        mock_genai = MagicMock()
        mock_genai.models.generate_content.return_value = MagicMock(
            text="APPROVED: Grounded response verified against Altostrat Singapore Policy (§8.3 / §12.1 / §14.2). Vacation balances and policy citations certified."
        )
        monkeypatch.setattr(genai, "Client", lambda *args, **kwargs: mock_genai)
    except ImportError:
        pass
