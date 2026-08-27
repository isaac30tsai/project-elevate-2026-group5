# Cloud KMS CMEK for AES-256-GCM Envelope Encryption & Cloud Firestore

resource "google_kms_key_ring" "agent_keyring" {
  name     = "altostrat-hr-agent-keyring-${var.environment}"
  location = var.region
  depends_on = [google_project_service.gemini_enterprise_apis]
}

resource "google_kms_crypto_key" "envelope_key" {
  name            = "altostrat-hr-agent-envelope-key"
  key_ring        = google_kms_key_ring.agent_keyring.id
  rotation_period = "31536000s" # 365 Days per SDD §4.2

  purpose = "ENCRYPT_DECRYPT"
  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }
}

resource "google_firestore_database" "agent_db" {
  project     = var.project_id
  name        = "altostrat-hr-agent-db-${var.environment}"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  concurrency_mode                = "OPTIMISTIC"
  app_engine_integration_mode     = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state         = "DELETE_PROTECTION_DISABLED"

  depends_on = [google_project_service.gemini_enterprise_apis]
}
