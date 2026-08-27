---
name: publish
description: Publishes deployed agents to Gemini Enterprise assistants and registers catalog metadata.
---

# Gemini Enterprise Publishing Skill

## Overview
Registers a provisioned Vertex AI Reasoning Engine or A2A container into Gemini Enterprise (`tpe-elevate-training`) front-door assistants.

## Pre-requisites
1. Target Agent deployed to Agent Runtime or Cloud Run.
2. Verified Gemini Enterprise App ID:
   `projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486`

## Execution Workflow
```bash
agents-cli publish gemini-enterprise \
  --gemini-enterprise-app-id "$GEMINI_ENTERPRISE_APP_ID" \
  --display-name "$DISPLAY_NAME" \
  --description "$DESCRIPTION" \
  --project $PROJECT_ID
```

## Direct Discovery Engine REST Upsert
When invoking programmatically via Discovery Engine v1alpha API:
`POST https://discoveryengine.googleapis.com/v1alpha/{APP_ID}/assistants/default_assistant/agents?agentId={AGENT_ID}`
