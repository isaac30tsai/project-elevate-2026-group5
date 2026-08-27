# Gemini Enterprise Front-Door Integration & Workspace Client Tier

resource "google_project_service" "gemini_enterprise_apis" {
  for_each = toset([
    "cloudaicompanion.googleapis.com",
    "discoveryengine.googleapis.com",
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "modelarmor.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudkms.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com"
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# Secret Manager for FastMCP Token
resource "google_secret_manager_secret" "mcp_token_secret" {
  secret_id = var.mcp_auth_token_secret
  replication {
    auto {}
  }
  depends_on = [google_project_service.gemini_enterprise_apis]
}

resource "google_secret_manager_secret_version" "mcp_token_secret_val" {
  secret      = google_secret_manager_secret.mcp_token_secret.id
  secret_data = "mcp_awThuI7rWgonvsSO4WInzJ9IgB-yAT4kjALp200kFDA"
}
