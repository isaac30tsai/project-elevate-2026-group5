---
name: observability
description: Configures OpenTelemetry distributed tracing and BigQuery FinOps token accounting.
---

# 4-Tier Observability & FinOps Skill

## Overview
Deploys and verifies the 4-tier telemetry pipeline across Cloud Trace, PII message protection, and BigQuery analytics.

## Verification Workflow
1. Verify BigQuery table status:
   `bq show --format=prettyjson ${PROJECT_ID}:altostrat_hr_analytics.compliance_audit_log`
2. Inspect Cloud Trace spans:
   `gcloud trace spans list --project=${PROJECT_ID}`
3. FinOps token audit query:
   ```sql
   SELECT
     event_timestamp,
     employee_id,
     mcp_tool_name,
     prompt_token_count,
     candidates_token_count,
     total_token_count,
     estimated_cost_usd
   FROM `${PROJECT_ID}.altostrat_hr_analytics.compliance_audit_log`
   ORDER BY event_timestamp DESC
   LIMIT 10;
   ```
