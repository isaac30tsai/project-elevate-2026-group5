# Vertex AI Search & Hybrid Knowledge Engine (§6-§35 Handbook)

resource "google_discovery_engine_data_store" "hr_policy_datastore" {
  provider                    = google-beta
  project                     = var.project_id
  location                    = "global"
  data_store_id               = "altostrat-hr-policy-datastore-${var.environment}"
  display_name                = "Altostrat Singapore HR Policy Handbook (§6-§35)"
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false

  depends_on = [google_project_service.gemini_enterprise_apis]
}

resource "google_discovery_engine_search_engine" "hr_search_engine" {
  provider                    = google-beta
  project                     = var.project_id
  location                    = "global"
  engine_id                   = "altostrat-hr-search-engine-${var.environment}"
  collection_id               = "default_collection"
  data_store_ids              = [google_discovery_engine_data_store.hr_policy_datastore.data_store_id]
  display_name                = "Altostrat HR Policy Grounding Engine"
  industry_vertical           = "GENERIC"
  common_config {
    company_name = "Altostrat Singapore"
  }
  search_engine_config {
    search_tier = "SEARCH_TIER_ENTERPRISE"
    search_add_ons = ["SEARCH_ADD_ON_LLM"]
  }
}
