# Vertex AI Agent Runtime & Reasoning Engine Operating Rules

## Core Principles
1. **Target Architecture**: Always deploy enterprise agents to Vertex AI Agent Runtime (`reasoningEngines`) using Google ADK (`google-adk >= 2.5.0`).
2. **Global Model Routing**: When deploying to regional locations (e.g., `asia-southeast1`), model resolution must be routed globally by setting `GOOGLE_CLOUD_LOCATION=global` and `GOOGLE_GENAI_USE_VERTEXAI=true`.
3. **Session Management**: Use `agent_platform_sessions` for scalable state persistence, memory continuity, and managed conversation context.
4. **Concurrency & Autoscaling**:
   - Default container concurrency: 8 concurrent streams per instance.
   - Autoscaling range: min instances = 0 (scale to zero), max instances = 10.
   - Resource limits: CPU = 1 vCPU, Memory = 4GiB.

## Operation & LRO Rules
- Vertex AI Agent Runtime provisioning is asynchronous via Long-Running Operations (LRO).
- Always track operation state using `projects/<PROJECT_NUM>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>/operations/<OP_ID>`.
- For troubleshooting, inspect Google Cloud Logging with filter:
  `resource.labels.reasoning_engine_id="<ENGINE_ID>"`
