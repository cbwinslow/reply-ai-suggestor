# Project summary — Reply AI Suggester

Goal

Build a low-friction AI assistant that suggests replies inline while users type on mobile (Android). The assistant should be highly configurable, privacy-conscious, and support multiple personalities/agents.

Key constraints

- Privacy: explicit consent for message access and personalization. Prefer InputMethodService (IME) to minimize sensitive permissions.
- UX: minimal, non-intrusive UI integrated with keyboard.
- Monetization: subscription tiers enabling higher-capacity personalization and higher-quality model options.

What we've implemented (so far)

- Project scaffold with Android Compose skeleton and a FastAPI mock backend.
- Networking client (`NetworkClient.kt`) wired into Compose UI.
- IME prototype registration and `KeyboardStubService` placeholder.
- Backend improvements: CORS, /health, intensity-aware mock suggestions, test helper.
- Documentation skeleton and privacy checklist.

Decisions already made (rationale)

1. Start with IME approach (InputMethodService) rather than Accessibility overlay to reduce Play Store risk and give users direct control over typed text.
2. Start with a cloud-backed model for prototyping (FastAPI mock) and make the model interface pluggable so we can swap in hosted or on-device providers.
3. Use local-first personalization with opt-in upload to server for fine-tuning.

Open decisions (to choose next)

- Model provider: hosted LLM (Gemini, Qwen, OpenAI) vs on-device small LLM. Tradeoffs: latency, cost, privacy.
- Personalization architecture: server-side fine-tuning vs retrieval-augmented generation (RAG) with per-user embeddings.
- Monetization & tier features (what features belong to which paid tier).

Immediate next milestone (2–3 weeks)

1. Implement consent flow and encrypted local store for personalization examples.
2. Replace networking with OkHttp + coroutines for reliability and clean threading.
3. Implement a production-grade IME UI that surfaces a suggestion strip and can commit/preview suggestions.
4. Wire a hosted model provider behind the backend provider abstraction (simple API adapter).
5. Run acceptance tests on emulator and device; prepare Play Store policy checklist.

Longer-term milestones (3–9 months)

- Per-user fine-tuning or RAG pipelines.
- Billing/subscription integration and gating for high-capacity features.
- Analytics and A/B testing (privacy-safe, opt-in).
- Marketplace for agents/personalities (careful review process).

Risks & mitigations

- Play Store policy: avoid using Accessibility for core functionality; prefer IME. If Accessibility is needed, prepare explicit policy justification and minimize use.

## Documentation edit policy

All repository documentation is governed by the project's append-only edit policy. Do not modify or delete existing documents without explicit written approval from a project approver. Allowed unapproved changes:

- Appending new entries to `tasks.md` or journal files.
- Adding new documents that do not alter existing documents in-place.

To deprecate content, strike it through and append the replacement with a short rationale and date (e.g., "~~Old text~~ (superseded 2025-10-31 by decision X)").

--
*Document last updated: 2025-10-31*
- Privacy: default to local-only; require explicit opt-in before uploading messages. Provide deletion and export tools.
- Cost: hosted LLM usage can be costly; provide throttles, fallbacks to cheaper models, and caching.

Contact and next steps

If you want, I will: implement the consent/local-store flow next (recommended), or implement OkHttp + coroutines networking and a settings UI to configure backend host and agent options. Which do you prefer?
