# Gemini Enterprise Front-Door Integration & Google Workspace Chat App

resource "google_project_service" "gemini_enterprise_apis" {
  for_each = toset([
    "cloudaicompanion.googleapis.com", # Gemini Enterprise / Gemini for Workspace
    "chat.googleapis.com",              # Google Workspace Chat API
    "discoveryengine.googleapis.com",   # Vertex AI Search & Conversation / Agent Engine
    "run.googleapis.com",               # Cloud Run Agent Runtime
    "aiplatform.googleapis.com",        # Vertex AI GenAI Platform
    "modelarmor.googleapis.com",        # Model Armor Prompt Shield
    "secretmanager.googleapis.com",     # Secret Manager for SaaS MCP tokens
    "cloudkms.googleapis.com",          # Cloud KMS CMEK for Envelope Encryption
    "firestore.googleapis.com",         # Cloud Firestore (Native)
    "bigquery.googleapis.com",          # BigQuery Compliance Lakehouse
    "pubsub.googleapis.com"             # Pub/Sub for asynchronous Chat App events
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# Vertex AI Conversation / Gemini Enterprise Chat Engine
resource "google_discovery_engine_chat_engine" "hr_chat_engine" {
  provider                    = google-beta
  project                     = var.project_id
  location                    = "global"
  engine_id                   = "tpe-elevate-group5-agent"
  collection_id               = "default_collection"
  data_store_ids              = [google_discovery_engine_data_store.hr_policy_datastore.data_store_id]
  display_name                = "tpe-elevate-group5-agent"
  industry_vertical           = "GENERIC"

  common_config {
    company_name = "Altostrat Singapore"
  }

  chat_engine_config {
    agent_creation_config {
      business              = "Altostrat Singapore Technology"
      default_language_code = "en"
      time_zone             = "Asia/Singapore"
    }
  }

  depends_on = [
    google_project_service.gemini_enterprise_apis,
    google_discovery_engine_data_store.hr_policy_datastore
  ]
}

# Automated Gemini Enterprise Agent Registration for tpe-elevate-training Front Door
resource "null_resource" "gemini_enterprise_agent_registration" {
  triggers = {
    service_url = google_cloud_run_v2_service.hr_agent_service.uri
  }

  provisioner "local-exec" {
    command = <<EOT
      python3 -c '
import subprocess, json

token = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()
url = "https://discoveryengine.googleapis.com/v1alpha/projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486/assistants/default_assistant/agents?agentId=tpe-elevate-group5-agent"

agent_card = {
    "protocolVersion": "0.3.0",
    "name": "tpe-elevate-group5-agent",
    "description": "Altostrat Singapore HR & IT Autonomous Assistant",
    "url": "${google_cloud_run_v2_service.hr_agent_service.uri}",
    "version": "1.0.0",
    "capabilities": {"streaming": False},
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [
        {"id": "hr-policy-qa", "name": "HR Policy Q&A", "description": "Grounded Singapore HR handbook policies Sections 6 to 35", "tags": ["hr", "policy", "handbook"]},
        {"id": "workweek-hcm", "name": "WorkWeek HCM Leave Management", "description": "Check leave balances and request time off", "tags": ["leave", "vacation", "sick"]},
        {"id": "service-immediately", "name": "ServiceImmediately ITSM Ticketing", "description": "Create and inspect IT support incident tickets", "tags": ["it", "incident", "ticket"]}
    ]
}

payload = {
    "displayName": "tpe-elevate-group5-agent",
    "description": "Altostrat Singapore HR & IT Autonomous Assistant powered by Gemini 3.5 Flash",
    "icon": {"uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/smart_toy/default/24px.svg"},
    "a2aAgentDefinition": {"jsonAgentCard": json.dumps(agent_card)}
}

subprocess.run(["curl", "-s", "-X", "POST", "-H", f"Authorization: Bearer {token}", "-H", "X-Goog-User-Project: ${var.project_id}", "-H", "Content-Type: application/json", "-d", json.dumps(payload), url], check=True)
'
    EOT
  }

  depends_on = [
    google_cloud_run_v2_service.hr_agent_service
  ]
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

# IAM Permissions for Google Workspace Chat App to invoke Cloud Run Agent Runtime
resource "google_cloud_run_v2_service_iam_member" "chat_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.hr_agent_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:chat-api-push@system.gserviceaccount.com"
}
