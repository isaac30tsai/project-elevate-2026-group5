# Enterprise Security Guardrails & Cryptographic Rules

## Mandatory Security Invariants
1. **Google Cloud Model Armor (<50ms)**:
   - Every user prompt must be screened before entering the cognitive reasoning loop.
   - Any prompt injection, jailbreak pattern, or unauthorized ID access must be immediately neutralized (`BLOCKED`).
2. **Server-Side Identity Injection (D-006)**:
   - The authenticated employee identity (`employee_id`) must NEVER be accepted from raw LLM parameter schemas.
   - Identity is resolved server-side from validated Google IAP or OIDC JWT bearer tokens and injected by tool execution wrappers.
3. **Application-Layer Envelope Encryption (D-004)**:
   - Sensitive session transcripts stored in Firestore must be encrypted using AES-256-GCM authenticated encryption (AEAD).
   - Ephemeral 256-bit Data Encryption Keys (DEKs) must be wrapped by Google Cloud KMS Key Encryption Keys (KEKs).
4. **Deterministic DFA Guardrails (D-008)**:
   - Business rules (e.g., leave balances `days <= accrued - used`, retroactive sick leave `max -14 days`, ITSM priority transitions) must be deterministically enforced by code, not left to LLM discretion.
