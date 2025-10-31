# Qwen model considerations (Qwen-series)

Overview

Qwen are models from Alibaba/Anyscale ecosystem (Qwen-7B-QA, Qwen-2, etc.). They provide hosted and sometimes on-prem or private deployments.

Pros
- Competitive performance-to-cost ratio for some Qwen variants.
- Some providers offer private or self-hosted deployment options to meet privacy requirements.

Cons
- Ecosystem and availability depend on provider; integrations vary.
- Fine-tuning and adapter tooling may be less mature compared to the largest providers.

Integration approach

- Same provider adapter pattern as Gemini: backend accepts SuggestRequest and forwards to provider.
- For on-prem/private deployments, coordinate hosting, scaling and GPU resources.

Personalization

- RAG is again a practical first step: compute per-user embeddings (open-source embeddings) and run a lightweight retriever on the server.
- For on-prem setups, store embeddings in a small vector DB (e.g., SQLite+FAISS or Milvus) with encryption at rest.

Cost & infra

- Evaluate price per token and expected queries per user to estimate monthly costs.
- Provide tiered plans: local-only, standard cloud model, high-quality model with fine-tuning.

Safety and compliance

- Apply the same moderation and sanitization processes as with other providers.
- For regulated customers, prefer private deployment or on-device-only options.

## Documentation edit policy

Important: This provider documentation is covered by the repository's documentation edit policy. Do not edit or delete this file without explicit written approval from a project approver. You may append notes, journals, or link to new provider-specific implementation notes, but do not change historical content in-place. If a section must be changed, strike through the old content and append the replacement with a short rationale and date.

## Provider housekeeping suggestions

- When implementing a Qwen provider adapter, add a `providers/qwen/README.md` that documents:
	- Required credentials and recommended deployment patterns
	- Cost expectations and fallback rules
	- Retrieval / RAG integration notes and embedding store recommendations
- Include an integration test that can be run locally with mocked credentials.

--
*Document last updated: 2025-10-31*
