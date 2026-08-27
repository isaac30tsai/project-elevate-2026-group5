output "cloud_run_agent_url" {
  description = "Cloud Run Agent Runtime Serving URL"
  value       = google_cloud_run_v2_service.hr_agent_service.uri
}

output "vertex_search_datastore_id" {
  description = "Vertex AI Search Data Store ID"
  value       = google_discovery_engine_data_store.hr_policy_datastore.data_store_id
}

output "kms_envelope_key_id" {
  description = "Cloud KMS Envelope Key ID"
  value       = google_kms_crypto_key.envelope_key.id
}

output "firestore_database_name" {
  description = "Firestore Native Database Name"
  value       = google_firestore_database.agent_db.name
}

output "bigquery_compliance_table" {
  description = "BigQuery Compliance Audit Log Table"
  value       = "${google_bigquery_dataset.hr_analytics_dataset.dataset_id}.${google_bigquery_table.compliance_audit_log.table_id}"
}
