#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT:-junho-elevate}"
REGION="${GCP_REGION:-asia-southeast1}"
SERVICE_NAME="altostrat-hr-agent"
MCP_TOKEN="${MCP_AUTH_TOKEN:-mcp_awThuI7rWgonvsSO4WInzJ9IgB-yAT4kjALp200kFDA}"

echo "================================================================================"
echo "  Deploying Altostrat HR & IT Agentic Solution to Argolis Project: ${PROJECT_ID}"
echo "================================================================================"

# 1. Enable all required Google Cloud APIs (including Cloud Build and Discovery Engine)
echo "1. Enabling required Google Cloud APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  cloudaicompanion.googleapis.com \
  discoveryengine.googleapis.com \
  chat.googleapis.com \
  run.googleapis.com \
  aiplatform.googleapis.com \
  modelarmor.googleapis.com \
  secretmanager.googleapis.com \
  cloudkms.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Store MCP Auth Token in Secret Manager
echo "2. Configuring Secret Manager for FastMCP Token..."
if ! gcloud secrets describe altostrat-mcp-token --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud secrets create altostrat-mcp-token --replication-policy="automatic" --project="${PROJECT_ID}"
fi
echo -n "${MCP_TOKEN}" | gcloud secrets versions add altostrat-mcp-token --data-file=- --project="${PROJECT_ID}"

# 3. Deploy Cloud Run Service
echo "3. Deploying Cloud Run Agent Runtime Service..."
gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source="." \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},GCP_REGION=${REGION},GEMINI_MODEL=gemini-3.7-flash,ENVIRONMENT=dev,WORKWEEK_BASE_URL=https://mock-saas.aishprabhat.demo.altostrat.com/work-week/mcp/,SERVICE_IMMEDIATELY_BASE_URL=https://mock-saas.aishprabhat.demo.altostrat.com/service-immediately/mcp/,MCP_AUTH_TOKEN=${MCP_TOKEN}" \
  --min-instances=1 \
  --max-instances=5 \
  --concurrency=80 \
  --memory=2Gi \
  --cpu=2 \
  --allow-unauthenticated

# 4. Display service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)")
echo "--------------------------------------------------------------------------------"
echo "Deployment Complete!"
echo "Agent Serving URL: ${SERVICE_URL}"
echo "Gemini Enterprise Webhook Endpoint: ${SERVICE_URL}/gemini-enterprise/chat"
echo "OpenAPI Spec Endpoint: ${SERVICE_URL}/openapi.json"
echo "================================================================================"
