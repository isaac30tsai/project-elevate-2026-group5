# 4-Tier Observability & FinOps Governance Rules

## Tier Specifications
1. **Tier 1 (Cloud Trace)**:
   - Export spans via OpenTelemetry (`OTEL_TRACES_EXPORTER=gcp_trace`).
   - Propagate unified `trace_id` across ingress API, safety gates, LLM cognitive loop, and tools.
2. **Tier 2 (Sensitive Data Redaction)**:
   - Strictly enforce `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`.
   - Never serialize raw prompts or confidential employee personal data into trace span attributes.
3. **Tier 3 (BigQuery FinOps Accounting)**:
   - Record token metrics (`prompt_token_count`, `thoughts_token_count`, `candidates_token_count`, `total_token_count`).
   - Calculate USD inference cost dynamically based on model pricing (Gemini 3.5 Flash: $0.075 / 1M in, $0.30 / 1M out).
   - Stream insert into day-partitioned table with automated 90-day retention (`expiration_ms = 7776000000`).
4. **Tier 4 (OTLP Interoperability)**:
   - Expose standard OpenTelemetry Collector endpoints for third-party APM tools (Phoenix, AgentOps, Datadog).
