# Cloud Run Agent Runtime for Dual-Agent Producer-Critic Architecture

resource "google_cloud_run_v2_service" "hr_agent_service" {
  name     = "altostrat-hr-agent-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.hr_agent_sa.email

    scaling {
      min_instance_count = 2 # 08:00 SGT Pre-warming per SDD §7.3
      max_instance_count = 10
    }

    max_instance_request_concurrency = 80

    containers {
      image = "gcr.io/${var.project_id}/altostrat-hr-agent:latest"

      resources {
        limits = {
          cpu    = "2000m"
          memory = "4Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "GCP_PROJECT"
        value = var.project_id
      }
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "DATASTORE_ID"
        value = google_discovery_engine_data_store.hr_policy_datastore.data_store_id
      }
      env {
        name  = "KMS_KEY_ID"
        value = google_kms_crypto_key.envelope_key.id
      }
      env {
        name  = "FIRESTORE_DATABASE"
        value = google_firestore_database.agent_db.name
      }
      env {
        name  = "WORKWEEK_BASE_URL"
        value = "https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/"
      }
      env {
        name  = "SERVICE_IMMEDIATELY_BASE_URL"
        value = "https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/"
      }
      env {
        name = "MCP_AUTH_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.mcp_token_secret.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.gemini_enterprise_apis,
    google_secret_manager_secret_version.mcp_token_secret_val
  ]
}
