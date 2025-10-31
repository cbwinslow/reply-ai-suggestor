# Project Tasks (append-only task journal)

This file is the canonical, append-only tasks document for the Reply AI Suggester project. Do not delete entries. When a task or microgoal becomes irrelevant, mark it as superseded by striking it through and adding a short rationale + date. Use the checkboxes to indicate completion.

Format rules (must follow):
- Use a top-level section for each major area (e.g., Backend, Android, Docs, QA, Infra).
- Each microgoal is a single checkboxed item with a short description and an acceptance criteria subsection.
- Never remove a line. To deprecate, strike through text: ~~This line is superseded (reason, YYYY-MM-DD)~~.

## How to use

- Add new tasks by appending at the bottom. Keep them small and testable.
- When completing a microgoal, check the box and optionally add ` (completed YYYY-MM-DD by @username)` after the line.
- For large tasks, break into microgoals and track them individually.

---

## 1. Backend

- [ ] Start and verify FastAPI backend in development environment
  - Acceptance criteria: `uvicorn backend.main:app` runs on port 8000 (or configured port); `/health` returns 200; `/suggest` returns sample suggestions for a valid POST.

- [ ] Implement persistent personalization storage (dev->prod path)
  - Microgoals:
    - [ ] Design storage schema and encryption-at-rest approach (choice: secure DB or encrypted files)
      - Acceptance criteria: design doc with pros/cons and security notes added to `docs/`.
    - [ ] Implement development in-memory store with unit tests
      - Acceptance criteria: tests under `backend/tests/` validate upload/get/delete flows.
    - [ ] Implement production storage adapter with encryption and rotation plan
      - Acceptance criteria: PR with code, tests, and deployment notes; codacy/trivy scan passes (no critical vulns).

- [ ] Provider adapter abstraction and Gemini/Qwen adapters
  - Microgoals:
    - [ ] Define adapter interface (input/output contract) and add to `backend/providers/README.md`.
    - [ ] Implement a Gemini adapter (mocked for dev) with integration test
    - [ ] Implement a Qwen adapter (mocked for dev) with integration test
  - Acceptance criteria: `backend/main.py` can switch provider via config and provider adapters have tests.

## 2. Android (IME + App)

- [ ] Finish IME prototype UI (suggestion strip + commit flow)
  - Microgoals:
    - [ ] Implement Compose-based suggestion strip in `KeyboardStubService` or IME module
    - [ ] Allow tapping a suggestion to commit text into the input connection
    - [ ] Add accessibility labels and keyboard compatibility checks
  - Acceptance criteria: Running APK on emulator shows suggestion strip; tapping a suggestion inserts text in a target app.

- [ ] Replace `HttpURLConnection` with `OkHttp` + Kotlin coroutines for networking
  - Acceptance criteria: `NetworkClient` uses `OkHttp` with coroutine suspending functions and handles errors/timeouts; unit tests cover success/failure flows.

- [ ] Implement Local encrypted personalization store (Jetpack Security)
  - Microgoals:
    - [ ] Add `androidx.security:security-crypto` dependency to `android/app/build.gradle.kts`
    - [ ] Implement `PersonalizationStore` with `EncryptedSharedPreferences` or encrypted files
    - [ ] Add export/import and delete flows in `SettingsActivity`
  - Acceptance criteria: Personalization blobs stored encrypted, export yields encrypted file, delete removes local blobs.

## 3. Docs & Policy

- [ ] Lockdown documentation edit policy across repo
  - Acceptance criteria: `agents.md`, `gemini.md`, `qwen.md`, and `README.md` contain the edit policy header; `tasks.md` exists and is referenced.

- [ ] Create Play Store privacy & policy checklist
  - Microgoals:
    - [ ] Draft privacy policy text
    - [ ] Draft Play Store listing privacy statements and data handling disclosures
  - Acceptance criteria: Policy file added to `docs/privacy.md` and referenced in `README.md`.

## 4. QA, CI & Security

- [ ] Add backend unit tests and CI pipeline
  - Microgoals:
    - [ ] Add `backend/tests/test_suggest.py` (happy path + empty context)
    - [ ] Add GitHub Actions workflow to run tests on push/PR
  - Acceptance criteria: Tests pass in CI and PRs run tests automatically.

- [ ] Run codacy/trivy scan after any dependency change
  - Acceptance criteria: No critical vulnerabilities; any new high-severity issues are triaged and fixed before merging.

## 5. Housekeeping (repo hygiene)

- [ ] Add `providers/` README and top-level CONTRIBUTING notes
  - Acceptance criteria: `providers/README.md` explains how to add a provider, tests, and required approvals.

- [ ] Keep `tasks.md` append-only
  - Procedure: NEVER delete lines. To deprecate: ~~strike through~~ and add reason + date.

---

### Example of striking-out (do not remove lines)

~~- [ ] Old task that is superseded (superseded on 2025-10-31 by replan)~~

---

*File created: 2025-10-31*
