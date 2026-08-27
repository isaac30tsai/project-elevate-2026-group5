# Vertex AI Agent Runtime Deployment Report

## 1. Deployment Summary
* **Target Environment**: Google Cloud Vertex AI Agent Runtime (`reasoningEngines`)
* **Agent Identifier**: `tpe-elevate-group5-agent`
* **Agent Engine Resource ID**: `5083095031766581248`
* **Full Resource Name**: `projects/636377148299/locations/asia-southeast1/reasoningEngines/5083095031766581248`
* **Service Account**: `service-636377148299@gcp-sa-aiplatform-re.iam.gserviceaccount.com`
* **Framework**: Google ADK 2.5 (`google-adk`)
* **Model Engine**: Gemini 3.5 Flash (`gemini-3.5-flash`)
* **Regional Routing**: `asia-southeast1` (Model Location: `global`)

## 2. Infrastructure & Autoscaling Specifications
* **CPU Limit**: 1 vCPU
* **Memory Limit**: 4 GiB
* **Min Instances**: 0 (Scale to Zero)
* **Max Instances**: 10
* **Container Concurrency**: 8 parallel streams per instance

## 3. Observability & Telemetry Configuration
* `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`
* `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`
* `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`
* `GOOGLE_GENAI_USE_VERTEXAI=true`

## 4. Google Cloud Console Link
* [Vertex AI Agent Engine Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/asia-southeast1/agent-engines/5083095031766581248?project=junho-elevate)
