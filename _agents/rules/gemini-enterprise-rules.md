# Gemini Enterprise Publishing & Front-Door Integration Rules

## Discovery Engine Hierarchy
1. **Engine Resource Pattern**:
   `projects/<PROJECT_NUMBER>/locations/global/collections/default_collection/engines/<ENGINE_ID>`
2. **Assistant Endpoint**:
   All conversational front-door agents reside under `assistants/default_assistant/agents/<AGENT_ID>`.

## Registration Types
1. **Native ADK Reasoning Engine (`adk_agent_definition`)**:
   - Backed directly by Vertex AI Agent Runtime:
     ```json
     {
       "adk_agent_definition": {
         "tool_settings": { "tool_description": "<TOOL_SUMMARY>" },
         "provisioned_reasoning_engine": { "reasoning_engine": "<REASONING_ENGINE_RESOURCE>" }
       }
     }
     ```
2. **A2A HTTP Protocol (`a2aAgentDefinition`)**:
   - Backed by containerized HTTP endpoints serving the `.well-known/agent-card.json` schema.

## Publishing Constraints
- Display name must clearly identify team, purpose, and capability.
- Ensure all skills declare unique `id`, `name`, `description`, and `tags`.
- State must be explicitly verified as `ENABLED` upon upsert.
