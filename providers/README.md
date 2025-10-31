Provider adapters
=================

This folder contains provider adapter guidance and templates. Each provider adapter (Gemini, Qwen, OpenAI, etc.) should live under `providers/<provider-name>/` and include:

- `README.md` describing credentials, endpoint URLs, rate limits, and cost considerations.
- A minimal `integration_test.py` or Kotlin/Java equivalent under `providers/<provider>/tests/` that validates the adapter's request/response shape using mocked credentials.

Adapter contract
- Input: `SuggestRequest` JSON `{user_id, context, modes, intensity, user_profile_summary?}`
- Output: `SuggestResponse` JSON `{suggestions: [string], metadata?: {...}}`

Security
- Do not commit credentials to the repo. Use environment variables or secret managers in CI.

Approval
- Adding or modifying a provider adapter requires a documented security review and approval.

*Template created: 2025-10-31*
