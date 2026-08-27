"""Production Cryptographic AES-256-GCM CMEK Envelope Encryption with Google Cloud KMS."""
from typing import Dict, Any, Optional
import os
import base64
import json
import logging
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings

logger = logging.getLogger(__name__)

# Google Cloud KMS & Firestore SDKs
try:
    from google.cloud import kms_v1
    from google.cloud import firestore
    HAS_GCP_STORAGE_SDK = True
except ImportError:
    HAS_GCP_STORAGE_SDK = False

class FirestoreStorageError(RuntimeError):
    """Raised when an encrypted envelope fails to persist to Google Cloud Firestore."""
    pass

class KMSEncryptionError(RuntimeError):
    """Raised when Google Cloud KMS CMEK key wrapping fails."""
    pass

class KMSDecryptionError(RuntimeError):
    """Raised when Google Cloud KMS CMEK key unwrapping fails."""
    pass

class FirestoreCryptoManager:
    """Two-tier CMEK Envelope Encryption Manager using AES-256-GCM and Google Cloud KMS."""

    def __init__(self, kms_key_id: Optional[str] = None, firestore_db: Optional[str] = None):
        self.project = settings.gcp_project
        self.region = settings.region
        self.kms_key_name = kms_key_id or (
            f"projects/{self.project}/locations/{self.region}/keyRings/altostrat-hr-keyring/cryptoKeys/altostrat-hr-transcript-key"
        )
        self.db_name = firestore_db or settings.firestore_db
        
        self.kms_client = None
        self.firestore_client = None
        
        if HAS_GCP_STORAGE_SDK and settings.environment not in ["test"]:
            try:
                self.kms_client = kms_v1.KeyManagementServiceClient()
            except Exception as e:
                logger.warning(f"Cloud KMS Client initialization failed: {e}")
            try:
                self.firestore_client = firestore.Client(project=self.project, database=self.db_name)
            except Exception as e:
                logger.debug(f"Cloud Firestore Client initialization fallback: {e}")

    def _wrap_dek_with_kms(self, raw_dek: bytes) -> str:
        """Wrap 256-bit DEK using Google Cloud KMS KEK (Key Encryption Key).
        
        Strict CMEK Envelope Encryption: Insecure local XOR masking fallbacks
        are strictly prohibited to prevent cryptographic boundary bypasses.
        """
        if not self.kms_client:
            raise KMSEncryptionError(
                "Google Cloud KMS client is not initialized. Insecure local XOR masking fallback "
                "is strictly prohibited by CMEK security policy."
            )
        try:
            response = self.kms_client.encrypt(
                request={
                    "name": self.kms_key_name,
                    "plaintext": raw_dek
                }
            )
            return base64.b64encode(response.ciphertext).decode("utf-8")
        except Exception as e:
            error_msg = f"Cloud KMS CMEK encryption failed for key '{self.kms_key_name}': {e}"
            logger.error(error_msg, exc_info=True)
            raise KMSEncryptionError(error_msg) from e

    def _unwrap_dek_with_kms(self, wrapped_dek_b64: str) -> bytes:
        """Unwrap encrypted DEK using Google Cloud KMS.
        
        Strict CMEK Envelope Encryption: Insecure local XOR masking fallbacks
        are strictly prohibited to prevent cryptographic boundary bypasses.
        """
        if not self.kms_client:
            raise KMSDecryptionError(
                "Google Cloud KMS client is not initialized. Insecure local XOR masking fallback "
                "is strictly prohibited by CMEK security policy."
            )
        try:
            wrapped_bytes = base64.b64decode(wrapped_dek_b64)
            response = self.kms_client.decrypt(
                request={
                    "name": self.kms_key_name,
                    "ciphertext": wrapped_bytes
                }
            )
            return response.plaintext
        except Exception as e:
            error_msg = f"Cloud KMS CMEK decryption failed for key '{self.kms_key_name}': {e}"
            logger.error(error_msg, exc_info=True)
            raise KMSDecryptionError(error_msg) from e

    def encrypt_transcript(self, raw_transcript: Dict[str, Any], fail_silently: bool = True) -> Dict[str, Any]:
        """Cryptographically encrypt conversation transcript using real AES-256-GCM."""
        session_id = raw_transcript.get("session_id", "session-default")
        employee_id = raw_transcript.get("employee_id", "EMP-558")
        
        # 1. Generate 256-bit (32-byte) Data Encryption Key (DEK)
        dek = AESGCM.generate_key(bit_length=256)
        
        # 2. Generate 96-bit (12-byte) standard GCM nonce/IV
        nonce = os.urandom(12)
        
        # 3. Authenticated Additional Data (AAD) binding to session & employee
        aad = f"{session_id}:{employee_id}".encode("utf-8")
        
        # 4. Perform true AES-256-GCM AEAD encryption
        aesgcm = AESGCM(dek)
        plaintext_bytes = json.dumps(raw_transcript).encode("utf-8")
        ciphertext_and_tag = aesgcm.encrypt(nonce, plaintext_bytes, aad)
        
        # 5. Wrap the DEK with Cloud KMS CMEK
        wrapped_dek_b64 = self._wrap_dek_with_kms(dek)
        
        envelope = {
            "session_id": session_id,
            "employee_id": employee_id,
            "algorithm": "AES-256-GCM",
            "ciphertext": base64.b64encode(ciphertext_and_tag).decode("utf-8"),
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "wrapped_dek": wrapped_dek_b64,
            "kms_key_version": f"{self.kms_key_name}/cryptoKeyVersions/1",
            "authenticated_data": base64.b64encode(aad).decode("utf-8"),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        }

        # 6. Write to Firestore if connected
        if self.firestore_client:
            try:
                doc_ref = self.firestore_client.collection("interaction_records").document(session_id)
                doc_ref.set(envelope)
                envelope["storage_status"] = "PERSISTED"
            except Exception as e:
                error_msg = f"Failed to persist encrypted envelope to Firestore for session '{session_id}' (employee '{employee_id}'): {e}"
                logger.error(error_msg, exc_info=True)
                envelope["storage_status"] = "PERSISTENCE_FAILED"
                envelope["storage_error"] = str(e)
                if not fail_silently:
                    raise FirestoreStorageError(error_msg) from e
        else:
            envelope["storage_status"] = "OFFLINE_ENCRYPTED_ONLY"

        return envelope

    def decrypt_transcript(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt envelope ciphertext back to original plaintext dictionary."""
        # 1. Unwrap DEK with KMS
        dek = self._unwrap_dek_with_kms(envelope["wrapped_dek"])
        
        # 2. Extract nonce and ciphertext
        nonce = base64.b64decode(envelope["nonce"])
        ciphertext_and_tag = base64.b64decode(envelope["ciphertext"])
        aad = base64.b64decode(envelope["authenticated_data"])
        
        # 3. Decrypt with AES-256-GCM
        aesgcm = AESGCM(dek)
        plaintext = aesgcm.decrypt(nonce, ciphertext_and_tag, aad)
        return json.loads(plaintext.decode("utf-8"))
