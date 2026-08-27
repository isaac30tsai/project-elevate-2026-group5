# BigQuery Compliance Lakehouse with 90-Day Partition Expiration

resource "google_bigquery_dataset" "hr_analytics_dataset" {
  dataset_id                  = "altostrat_hr_analytics"
  friendly_name               = "Altostrat HR Compliance & Audit Analytics"
  description                 = "Centralized audit logs with automated 90-day partition expiration"
  location                    = var.region
  default_table_expiration_ms = 7776000000 # 90 days

  access {
    role          = "OWNER"
    user_by_email = google_service_account.hr_agent_sa.email
  }
  depends_on = [google_project_service.gemini_enterprise_apis]
}

resource "google_bigquery_table" "compliance_audit_log" {
  dataset_id          = google_bigquery_dataset.hr_analytics_dataset.dataset_id
  table_id            = "compliance_audit_log"
  description         = "Audit logs partitioned by event_timestamp with clustering by employee_id"
  deletion_protection = false

  time_partitioning {
    type                     = "DAY"
    field                    = "event_timestamp"
    expiration_ms            = 7776000000 # 90 days
    require_partition_filter = true
  }

  clustering = ["employee_id", "event_type"]

  schema = jsonencode([
    {
      name: "event_id",
      type: "STRING",
      mode: "REQUIRED",
      description: "Unique event UUID"
    },
    {
      name: "event_timestamp",
      type: "TIMESTAMP",
      mode: "REQUIRED",
      description: "UTC event timestamp - Partition Key"
    },
    {
      name: "employee_id",
      type: "STRING",
      mode: "REQUIRED",
      description: "Masked Employee ID - Cluster Key"
    },
    {
      name: "employee_role",
      type: "STRING",
      mode: "REQUIRED",
      description: "Role at execution time"
    },
    {
      name: "event_type",
      type: "STRING",
      mode: "REQUIRED",
      description: "TOOL_EXEC | POLICY_QUERY | SAGA_ROLLBACK | RTBF_PURGE"
    },
    {
      name: "mcp_tool_name",
      type: "STRING",
      mode: "NULLABLE",
      description: "Invoked FastMCP tool name"
    },
    {
      name: "tool_parameters_masked",
      type: "JSON",
      mode: "NULLABLE",
      description: "DLP-sanitized parameter payload"
    },
    {
      name: "compliance_verdict",
      type: "STRING",
      mode: "REQUIRED",
      description: "PASSED | REDACTED | BLOCKED"
    },
    {
      name: "trace_id",
      type: "STRING",
      mode: "REQUIRED",
      description: "Cloud Trace distributed correlation ID"
    },
    {
      name: "prompt_token_count",
      type: "INTEGER",
      mode: "NULLABLE",
      description: "Input prompt token count for FinOps accounting"
    },
    {
      name: "candidates_token_count",
      type: "INTEGER",
      mode: "NULLABLE",
      description: "Output candidates token count"
    },
    {
      name: "thoughts_token_count",
      type: "INTEGER",
      mode: "NULLABLE",
      description: "Gemini 3.5 reasoning thought token count"
    },
    {
      name: "total_token_count",
      type: "INTEGER",
      mode: "NULLABLE",
      description: "Total token usage per transaction"
    },
    {
      name: "estimated_cost_usd",
      type: "FLOAT",
      mode: "NULLABLE",
      description: "Estimated inference cost in USD"
    },
    {
      name: "model_name",
      type: "STRING",
      mode: "NULLABLE",
      description: "Gemini model version string"
    },
    {
      name: "traffic_type",
      type: "STRING",
      mode: "NULLABLE",
      description: "ON_DEMAND | PROVISIONED"
    },
    {
      name: "latency_ms",
      type: "FLOAT",
      mode: "NULLABLE",
      description: "End-to-end execution latency in milliseconds"
    }
  ])
}
