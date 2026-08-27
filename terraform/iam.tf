# Least-Privilege IAM Service Accounts & Role Bindings

resource "google_service_account" "hr_agent_sa" {
  account_id   = "sa-altostrat-hr-agent-${var.environment}"
  display_name = "Altostrat HR Agentic Solution Runtime Service Account"
}

# Vertex AI User Role
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# Discovery Engine / Vertex Search Viewer
resource "google_project_iam_member" "discovery_engine_viewer" {
  project = var.project_id
  role    = "roles/discoveryengine.viewer"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# Firestore User Role
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# KMS Encrypter/Decrypter Role
resource "google_kms_crypto_key_iam_member" "kms_crypto_user" {
  crypto_key_id = google_kms_crypto_key.envelope_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# BigQuery Data Editor for Audit Plane
resource "google_project_iam_member" "bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# Secret Manager Accessor for FastMCP Token
resource "google_secret_manager_secret_iam_member" "secret_accessor" {
  secret_id = google_secret_manager_secret.mcp_token_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}
