# Gemini Enterprise Agent Registration & Publishing Report

## 1. Registration Overview
* **Agent Identifier**: `tpe-elevate-group5-agent`
* **Registration State**: `ENABLED`
* **Gemini Enterprise Tenant App**: `projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486`
* **Target Assistant**: `default_assistant`
* **Full Agent Resource Name**: `projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486/assistants/default_assistant/agents/tpe-elevate-group5-agent`
* **Registration Protocol**: A2A Protocol v0.3.0 (Agent-to-Agent) & OpenAPI 3.0.3

## 2. Live Runtime Endpoints
* **Cloud Run Backend Serving URL**: `https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app`
* **A2A Well-Known Agent Card**: `https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app/.well-known/agent-card.json`
* **Gemini Enterprise Webhook**: `https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app/gemini-enterprise/chat`
* **OpenAPI 3.0 Documentation**: `https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app/openapi.json`
* **Agent Registry Metadata**: `https://tpe-elevate-group5-agent-lydisbk46a-as.a.run.app/v1/agent/registry`

## 3. Dispatched Skills & Functional Capabilities
1. **`hr-policy-qa`**: Grounded Singapore HR Handbook Policy Q&A (§6 to §35) via Vertex AI Search (Discovery Engine).
2. **`workweek-hcm`**: Real-time leave balances and time-off request transaction submission with -14d retroactivity constraint.
3. **`service-immediately`**: ITSM hardware incident ticketing with automated P1-to-P4 business prioritization guardrail.

## 4. Verification Console
* **Gemini Enterprise Console**: [Agent Builder App Overview](https://console.cloud.google.com/gen-app-builder/engines?project=junho-elevate)
* **Cloud Run Console**: [Service Dashboard](https://console.cloud.google.com/run/detail/asia-southeast1/tpe-elevate-group5-agent?project=junho-elevate)
