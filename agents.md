# Agent design for Reply AI Suggester

This document describes the "agent" concept used in the app: how agents generate suggestions, how personalization interacts with agents, and how we can run multiple agents simultaneously.

1) Agent definition
- An agent is a configured prompt + behavior module that transforms an input context (recent typed text or message) into a set of replies.
- Each agent exposes configuration fields: style (casual/formal/witty), intensity (0-10), persona (short text), and resource budget (how many tokens or which model profile to use).

2) Agent types
- Core system agents (admin-provided): base personalities and safety filters.
- User agents: created or tuned by the user (saves preferences, persona snippets, example messages).
- Third-party agents (future): marketplace-provided personalities (subject to review and policy).

3) Execution model
- On each eligible typing event, the system evaluates whether to call agents based on "opportunity detection" heuristics (e.g., message length, trigger phrases, user settings). When triggered, selected agents run in parallel and return candidate suggestions.
- To reduce cost, use a light-weight on-device classifier to decide if an agent call is warranted; otherwise, deferred or batched calls are used.

4) Personalization and data flow
- Default: local-only personalization (store embeddings, example pairs locally in encrypted storage).
- Opt-in: if user allows, anonymized examples can be uploaded for server-side fine-tuning or per-user retrieval-augmented generation.
- Always expose delete/export controls.

5) Safety & moderation
- All suggestions pass a safety filter before display (on-device if possible; server-side if needed).
- Agents can have per-agent blocking/allow lists.

6) Multi-agent workflows
- Fan-out: run multiple agents in parallel and present the combined candidate list.
- Mix-and-match: provide UI to combine suggestions across agents (e.g., merge style of agent A with wording of agent B).

7) Developer contract (API)
- Input: {user_id, context, modes, intensity, user_profile_summary}
- Output: {suggestions: [string], scores?: [float], metadata?: {agent_id, tokens_used}}

8) Metrics
- Track per-agent acceptance rate, helpfulness (user taps/edits), and latency. Metrics must be privacy-preserving and opt-in.

9) Future: agent orchestration
- Add a lightweight planner that picks an ordered subset of agents to call based on user preferences, time-of-day patterns, and historical acceptance rates.

---

Notes: agent runtimes may be on-device (fast, private) or in the cloud (powerful, costly). The system should be modular to allow both approaches.

## Documentation edit policy

Important: The documentation in this repository is governed by a strict edit policy to preserve auditability and historical context.

- No documentation files (including but not limited to `agents.md`, `gemini.md`, `qwen.md`, `project_summary.md`, `SRS.md`, and files under `docs/`) are to be modified or deleted by anyone without explicit written approval from the project owners.
- The only permitted in-repo updates without prior approval are:
	- Appending new entries to the journals and the task lists (see `tasks.md`).
	- Adding new documents (clearly labeled and linked) that do not alter existing documents' contents.
- If an existing document needs to be updated (corrections, technical changes, or policy updates), open a PR with an explicit approval comment from a designated approver before merging.

When a change becomes irrelevant, it must not be deleted; instead, mark it as superseded by striking through the text and adding a short rationale and date. For example:

~~This line is no longer relevant (superseded on 2025-10-31 by decision X).~~

This keeps the repository append-only and audit-friendly.

## Housekeeping notes

- Keep a single canonical `tasks.md` at the repository root to track microgoals and progress (append-only with checkboxes). Do not remove completed entries; mark them as completed with the checkbox and optionally add a timestamp.
- When adding a new agent implementation or provider adapter, include:
	- A short README under `providers/<provider-name>/README.md` describing configuration, credentials required, rate limits and cost expectations.
	- An integration test under `backend/tests/` that validates the adapter's request/response shape (mocked credentials allowed).

--
*Document last updated: 2025-10-31*
