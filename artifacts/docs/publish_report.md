# Gemini Enterprise Agent Registration & Publishing Report

## 1. Registration Overview
* **Agent Identifier**: `tpe-elevate-group5-agent`
* **Registration Type**: `adkAgentDefinition` (Native Vertex AI Reasoning Engine)
* **Registration State**: `ENABLED`
* **Gemini Enterprise Tenant App**: `projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486`
* **Target Assistant**: `default_assistant`
* **Full Agent Resource Name**: `projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486/assistants/default_assistant/agents/tpe-elevate-group5-agent`

## 2. Vertex AI Agent Runtime Backend Binding
* **Provisioned Reasoning Engine**: `projects/636377148299/locations/asia-southeast1/reasoningEngines/5083095031766581248`
* **Model Engine**: Gemini 3.5 Flash (`gemini-3.5-flash`)
* **Tool Settings Description**: Autonomous HR & IT Assistant for Singapore: §6-§35 handbook grounding, WorkWeek leave balances, and ServiceImmediately ticketing

## 3. Dispatched Skills & Functional Capabilities
1. **`hr-policy-qa`**: Grounded Singapore HR Handbook Policy Q&A (§6 to §35) via Vertex AI Search.
2. **`workweek-hcm`**: Real-time leave balances and time-off request transaction submission with -14d retroactivity constraint.
3. **`service-immediately`**: ITSM hardware incident ticketing with automated P1-to-P4 business prioritization guardrail.

## 4. Verification Console Links
* **Gemini Enterprise Console**: [Agent Builder App Overview](https://console.cloud.google.com/gen-app-builder/engines?project=junho-elevate)
* **Vertex AI Agent Engine**: [Reasoning Engine Details](https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/asia-southeast1/agent-engines/5083095031766581248?project=junho-elevate)
