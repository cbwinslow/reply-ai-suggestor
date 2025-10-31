Software Requirements Specification (SRS)
Reply AI Suggester

Revision: 0.1
Date: 2025-10-31
Author: project team

1. Introduction

1.1 Purpose
This SRS describes the requirements for "Reply AI Suggester" — a mobile-first assistant that offers AI-generated reply suggestions inline while the user composes messages on Android. The SRS covers functional and non-functional requirements, data/privacy/security requirements, interfaces, constraints, and acceptance criteria.

1.2 Scope
The initial product is an Android app with a minimal backend for suggestion generation and personalization. Primary features include:
- IME (InputMethodService) integration to surface suggestion strip while typing.
- Multiple suggestion styles (casual, formal, witty) and adjustable intensity.
- Local-first personalization with opt-in cloud upload for improved personalization.
- Settings UI for consent, intensity, agent selection, and data controls.

1.3 Definitions
- IME: InputMethodService (Android keyboard service)
- Agent: a configured personality/module producing suggestions
- RAG: Retrieval-Augmented Generation

2. Overall description

2.1 Product perspective
Client-server architecture. The Android client communicates with a backend provider via HTTPS. The backend exposes a provider abstraction to plug-in hosted LLMs or local model endpoints. The client should be usable with an emulator during development and configurable to point at production endpoints.

2.2 User classes and characteristics
- End users: typical smartphone users who want reply suggestions.
- Admins: configure system-level agent defaults and safety filters.
- Developers/Integrators: run and extend the backend and model adapters.

2.3 Operating environment
- Android devices (minSdk: TBD; recommend 24+ initially).
- Backend: Python 3.10+ environment (FastAPI), optional hosting on cloud providers.

3. Functional requirements

FR-1: IME Suggestion Strip
- The app shall provide an IME that can be enabled by the user.
- The IME shall display up to N suggestions in a horizontal strip above the keyboard.
- The IME shall allow the user to accept a suggestion (commit into the current input), copy it, or edit before sending.

FR-2: Suggestion Generation
- The client shall POST SuggestRequest to the backend: {user_id, context, modes, intensity}.
- The backend shall respond with SuggestResponse: {suggestions: [string], metadata?}.
- The client shall display suggestion text immediately when response arrives.

FR-3: Agent Modes and Intensity
- The system shall support selectable modes (casual, formal, witty) and numeric intensity (0-10) that influence output.

FR-4: Consent & Data Controls
- The app shall present an explicit consent screen before collecting or uploading any message data for personalization.
- The app shall allow export and deletion of personalization data.

## Documentation edit policy

This SRS is governed by the repository's append-only documentation policy. Do not edit or delete the SRS without explicit written approval from a project approver. To update requirements, append changes and include a short rationale and date; do not overwrite historical items.

--
*Document last updated: 2025-10-31*

FR-5: Local Personalization
- The app shall store personalization artifacts locally, encrypted at rest, when user opts in.
- The app shall allow opt-in cloud upload for server-side personalization with explicit, recorded consent.

FR-6: Provider Abstraction
- The backend shall implement a provider adapter interface to support multiple LLM providers.

FR-7: Health & Diagnostics
- The backend shall expose a `/health` endpoint returning status information.

4. Non-functional requirements

NFR-1: Latency
- Suggestion generation round-trip (client to server and back) shall be < 1.5s for typical network conditions on recommended models. If backend latency is higher, UI should show a progress indicator and degrade gracefully.

NFR-2: Privacy
- By default, no text leaves the device for personalization unless the user explicitly opts in.
- Uploaded data must be encrypted in transit and stored under documented retention policies.

NFR-3: Security
- Client-server communication must use HTTPS with TLS 1.2+.
- Authentication for user-specific endpoints must be implemented (OAuth2/JWT) in later phases.

NFR-4: Scalability
- Backend design shall allow horizontal scaling for model-serving endpoints.

NFR-5: Robustness
- Client shall handle offline conditions: offer local fallback or present an appropriate message.

5. Data requirements
- User profile: minimal metadata (user_id, opt-in flags).
- Personalization store: embeddings, examples (context+response), timestamps (encrypted at rest).
- Logs: limited telemetry (opt-in) with no message contents.

6. Privacy & Legal
- Provide an in-app privacy policy and consent screen.
- Provide tools to export and delete collected personalization data.
- Avoid requesting SMS or call-log permissions unless necessary; prefer IME.

7. Interfaces
7.1 Client REST API to backend
- POST /suggest
  - Request: {user_id, context, modes, intensity}
  - Response: {suggestions: [string], metadata?: {...}}

- POST /train (optional): accept personalization payloads for server-side training.
- GET /health

7.2 User interface
- IME suggestion strip, settings screen, consent flow, and agent selector.

8. Acceptance criteria
- IME displays suggestions returned from the backend and allows accepting a suggestion.
- Consent screen must block personalization upload until granted.
- Personalization data can be deleted by the user.
- Basic backend endpoints respond to test requests (test script included).

9. Constraints
- Play Store policy may restrict the use of Accessibility APIs. Prefer IME route.
- Device storage space and on-device model sizes may limit on-device personalization and on-device LLM usage.

10. Future enhancements (non-normative)
- Server-side personalization and fine-tuning pipelines.
- Support for multiple agents and agent orchestration.
- On-device small LLM fallback for ultra-low-latency suggestions.

Appendix A: Glossary
- IME, RAG, LLM, Agent

Appendix B: Open items (to be finalized)
- Minimum Android API level
- Authentication scheme for user-specific endpoints
- Billing tiers and which features are gated

