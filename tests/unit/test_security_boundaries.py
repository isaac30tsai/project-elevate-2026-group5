import pytest
from unittest.mock import patch, MagicMock

from app.storage.firestore_crypto import (
    FirestoreCryptoManager,
    KMSEncryptionError,
    KMSDecryptionError,
    FirestoreStorageError
)
from app.security.oidc import OIDCIdentityResolver, OIDCAuthenticationError
from app.config import settings

def test_kms_cmek_strict_boundary_no_xor_fallback():
    """Verify that KMS failure raises KMSEncryptionError and NEVER falls back to local XOR masking."""
    manager = FirestoreCryptoManager()
    
    # 1. Simulate uninitialized or missing KMS client
    manager.kms_client = None
    with pytest.raises(KMSEncryptionError) as excinfo:
        manager._wrap_dek_with_kms(b"0" * 32)
    assert "local XOR masking fallback is strictly prohibited" in str(excinfo.value)

    # 2. Simulate KMS remote encryption permission / network error
    mock_kms = MagicMock()
    mock_kms.encrypt.side_effect = RuntimeError("KMS PermissionDenied: caller lacks cloudkms.cryptoKeyVersions.useToEncrypt")
    manager.kms_client = mock_kms

    with pytest.raises(KMSEncryptionError) as excinfo:
        manager._wrap_dek_with_kms(b"0" * 32)
    assert "Cloud KMS CMEK encryption failed" in str(excinfo.value)
    assert "PermissionDenied" in str(excinfo.value)


def test_kms_cmek_unwrap_strict_boundary():
    """Verify that KMS unwrapping failure raises KMSDecryptionError without XOR fallback."""
    manager = FirestoreCryptoManager()
    manager.kms_client = None
    
    with pytest.raises(KMSDecryptionError) as excinfo:
        manager._unwrap_dek_with_kms("invalid_base64_dek==")
    assert "local XOR masking fallback is strictly prohibited" in str(excinfo.value)


def test_oidc_rejects_invalid_or_unverified_token():
    """Verify that tokens with invalid cryptographic signatures are strictly rejected."""
    resolver = OIDCIdentityResolver()

    # 1. Arbitrary / forged JWT
    forged_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJlbWFpbCI6ImF0dGFja2VyQGdtYWlsLmNvbSIsImF1ZCI6InRlc3QtYXVkIiwiZXhwIjoyMDAwMDAwMDAwfQ.invalid_sig"
    valid, claims, msg = resolver.validate_bearer_jwt(forged_token)
    assert valid is False
    assert "verification failed" in msg.lower() or "signature" in msg.lower()

    # 2. Untrusted issuer
    untrusted_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2V2aWwtc3Bvb2Zlci5jb20iLCJlbWFpbCI6ImF0dGFja2VyQGV2aWwuY29tIiwiZXhwIjoyMDAwMDAwMDAwfQ.invalid_sig"
    valid, claims, msg = resolver.validate_bearer_jwt(untrusted_token)
    assert valid is False
    assert "untrusted token issuer" in msg.lower()


def test_oidc_rejects_unverified_body_spoofing_in_prod():
    """Verify that client body email cannot spoof identity without valid auth headers in prod."""
    resolver = OIDCIdentityResolver()
    
    with patch.object(settings, "environment", "prod"):
        headers = {}
        body = {"user": {"email": "ceo@altostrat.com"}}
        resolved = resolver.resolve_caller_identity(headers, body)
        # In prod, body email is rejected; returns default identity, not the spoofed CEO
        assert resolved != "EMP-001"
        assert resolved == "EMP-558"
