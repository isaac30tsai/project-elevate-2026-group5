# AGENTS.md — Altostrat HR & IT Autonomous Agent (Group 5)

## Workspace Scope & Purpose
This repository implements the production-grade **Altostrat HR & IT Agentic Solution (MVP 1)** for Singapore, built with Google ADK 2.0, Gemini 3.5 Flash, FastMCP tool servers, and Vertex AI Agent Runtime.

---

## Commands
* **Run Preflight Check**: `bash scripts/preflight_check.sh`
* **Run 4-Tier Golden Evaluation**: `python3 -m unittest eval_benchmark.py`
* **Deploy to Vertex AI Agent Runtime**: `agents-cli deploy --deployment-target agent_runtime --project ${GCP_PROJECT:-altostrat-elevate} --region asia-southeast1 --service-name tpe-elevate-group5-agent`
* **Publish to Gemini Enterprise**: `agents-cli publish gemini-enterprise --gemini-enterprise-app-id "projects/636377148299/locations/global/collections/default_collection/engines/tpe-elevate-training_1787798925486" --display-name "tpe-elevate-group5-agent"`
* **Local Gateway Server**: `python3 -m uvicorn app.main:app --port 8080`

---

## Core Architecture
```
tpe-elevate-group5-agent/
├── app/                           # Core Agent Application
│   ├── agent.py                   # Dual-Agent Producer-Critic reasoning loop
│   ├── config.py                  # Environment & model settings (gemini-3.5-flash)
│   ├── gemini_enterprise_adapter.py # Chat CardV2 & user identity extraction
│   ├── guardrails/model_armor.py  # Live Google Cloud Model Armor REST client
│   ├── observability/telemetry.py # 4-Tier OpenTelemetry distributed tracing
│   ├── security/oidc.py           # Cryptographic OIDC / IAP JWT claim validation
│   ├── storage/firestore_crypto.py# AES-256-GCM AEAD CMEK envelope encryption
│   ├── storage/bigquery_audit.py  # BigQuery FinOps token & cost accounting
│   └── tools/                     # RAG & FastMCP clients (WorkWeek, ServiceImmediately)
├── artifacts/docs/                # Official architectural verification reports
│   ├── publish_report.md          # Gemini Enterprise publishing report
│   └── observability_report.md    # 4-tier telemetry & FinOps specification
├── scripts/                       # Operational & preflight shell scripts
│   └── preflight_check.sh         # GCP environment validation probe
├── terraform/                     # Complete IaC automation
├── _agents/                       # Agent governance rules and specialized skills
│   ├── rules/                     # Architecture, security & publishing rules
│   └── skills/                    # Automated deployment, evaluation, and CE skills
├── agents-cli-manifest.yaml       # Vertex AI Agent Runtime configuration
└── SDD.md                         # Authoritative Solution Design Document
```

---

## Skills & Capabilities
* **`deployment`**: Automated deployment to Vertex AI Agent Runtime (`reasoningEngines`).
* **`publish`**: Registration into Gemini Enterprise (`tpe-elevate-training`) front-door assistants.
* **`evaluation`**: 4-Tier stratified golden benchmark evaluation harness.
* **`observability`**: Cloud Trace distributed tracing and BigQuery FinOps accounting.
* **`ce-tech`**: Google Cloud CE architecture blueprint validation and demonstration playbooks.

---

## Operating Rules & Constraints
* **English Only**: All files, commit messages, and documentation must be written strictly in 100% English.
* **Zero Emoji Noise**: Avoid decorative emojis in code, logs, and production documentation.
* **Grounding Citation Invariant**: Policy answers must cite official sections (§6 to §35).
* **Identity Isolation**: Authenticated `employee_id` must always be resolved server-side from OIDC/IAP JWT tokens and never accepted from LLM tool arguments.
* **Encryption Invariant**: Stored transcripts must use authenticated AES-256-GCM encryption with Cloud KMS KEK wrapping.
