---
name: deployment
description: Deploys ADK agents to Vertex AI Agent Runtime with autoscaling and 4-tier observability.
---

# Vertex AI Agent Runtime Deployment Skill

## Overview
Deploys Google ADK agents to Vertex AI Agent Runtime (`reasoningEngines`) using `agents-cli deploy`.

## Pre-requisites
1. Validate active GCP authentication: `gcloud config get-value account`.
2. Ensure required APIs are active: `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`.
3. Verify `agents-cli-manifest.yaml` contains `deployment_target: agent_runtime` and `base_template: adk`.

## Execution Workflow
```bash
agents-cli deploy \
  --deployment-target agent_runtime \
  --project $PROJECT_ID \
  --region $REGION \
  --service-name $AGENT_NAME
```

## Failure Recovery
- Query LRO state with `agents-cli deploy --status`.
- Inspect build logs:
  `gcloud logging read "resource.labels.reasoning_engine_id='$ENGINE_ID'" --limit=50`
