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

- [x] Start and verify FastAPI backend in development environment (completed 2025-10-31)
  - Acceptance criteria: `uvicorn backend.main:app` runs on port 8000 (or configured port); `/health` returns 200; `/suggest` returns sample suggestions for a valid POST.

- [x] Implement persistent personalization storage (dev->prod path) - GitHub Issue #6, GitLab Issue #6
  - Microgoals:
    - [ ] Design storage schema and encryption-at-rest approach (choice: secure DB or encrypted files)
      - Acceptance criteria: design doc with pros/cons and security notes added to `docs/`.
    - [ ] Implement development in-memory store with unit tests
      - Acceptance criteria: tests under `backend/tests/` validate upload/get/delete flows.
    - [ ] Implement production storage adapter with encryption and rotation plan
      - Acceptance criteria: PR with code, tests, and deployment notes; codacy/trivy scan passes (no critical vulns).

- [x] Provider adapter abstraction and Gemini/Qwen adapters - GitHub Issue #7, GitLab Issue #7
  - Microgoals:
    - [ ] Define adapter interface (input/output contract) and add to `backend/providers/README.md`.
    - [ ] Implement a Gemini adapter (mocked for dev) with integration test
    - [ ] Implement a Qwen adapter (mocked for dev) with integration test
  - Acceptance criteria: `backend/main.py` can switch provider via config and provider adapters have tests.

## 2. Android (IME + App)

- [x] Finish IME prototype UI (suggestion strip + commit flow) - GitHub Issue #8, GitLab Issue #8 (completed 2025-10-31)
  - Microgoals:
    - [x] Implement Compose-based suggestion strip in `KeyboardStubService` or IME module (completed 2025-10-31)
    - [x] Allow tapping a suggestion to commit text into the input connection (completed 2025-10-31)
    - [ ] Add accessibility labels and keyboard compatibility checks
  - Acceptance criteria: Running APK on emulator shows suggestion strip; tapping a suggestion inserts text in a target app.

- [x] Replace `HttpURLConnection` with `OkHttp` + Kotlin coroutines for networking (completed 2025-10-31)
  - Acceptance criteria: `NetworkClient` uses `OkHttp` with coroutine suspending functions and handles errors/timeouts; unit tests cover success/failure flows.

- [x] Implement Local encrypted personalization store (Jetpack Security) (completed 2025-10-31)
  - Microgoals:
    - [x] Add `androidx.security:security-crypto` dependency to `android/app/build.gradle.kts` (completed 2025-10-31)
    - [x] Implement `PersonalizationStore` with `EncryptedSharedPreferences` or encrypted files (completed 2025-10-31)
    - [x] Add export/import and delete flows in `SettingsActivity` (completed 2025-10-31)
  - Acceptance criteria: Personalization blobs stored encrypted, export yields encrypted file, delete removes local blobs.

## 3. Docs & Policy

- [x] Lockdown documentation edit policy across repo (completed 2025-10-31)
  - Acceptance criteria: `agents.md`, `gemini.md`, `qwen.md`, and `README.md` contain the edit policy header; `tasks.md` exists and is referenced.

- [x] Create Play Store privacy & policy checklist - GitHub Issue #10, GitLab Issue #10
  - Microgoals:
    - [ ] Draft privacy policy text
    - [ ] Draft Play Store listing privacy statements and data handling disclosures
  - Acceptance criteria: Policy file added to `docs/privacy.md` and referenced in `README.md`.

## 4. QA, CI & Security

- [x] Add backend unit tests and CI pipeline - GitHub Issue #9, GitLab Issue #9
  - Microgoals:
    - [ ] Add `backend/tests/test_suggest.py` (happy path + empty context)
    - [ ] Add GitHub Actions workflow to run tests on push/PR
  - Acceptance criteria: Tests pass in CI and PRs run tests automatically.

- [x] Run codacy/trivy scan after any dependency change (completed 2025-10-31)
  - Acceptance criteria: No critical vulnerabilities; any new high-severity issues are triaged and fixed before merging.

## 5. Housekeeping (repo hygiene)

- [ ] Add `providers/` README and top-level CONTRIBUTING notes
  - Acceptance criteria: `providers/README.md` explains how to add a provider, tests, and required approvals.

- [x] Keep `tasks.md` append-only (completed 2025-10-31)
  - Procedure: NEVER delete lines. To deprecate: ~~strike through~~ and add reason + date.

## 6. Project Management & Issues

- [x] Create GitHub issues using templates (completed 2025-10-31)
  - Issues created: IME UI Prototype (#1), Persistent Storage (#2), Provider Adapters (#3), Privacy Policy (#4), Backend Environment (#5), Storage Epic (#6), AI Adapters (#7), IME Completion (#8), Testing & CI (#9), Privacy Policy (#10)
  - Acceptance criteria: Issues created with proper templates, descriptions, and acceptance criteria.

- [x] Create GitLab issues mirroring GitHub (completed 2025-10-31)
  - Issues created: Same set as GitHub with identical content
  - Acceptance criteria: All GitHub issues mirrored to GitLab with proper labels.

- [x] Create project boards and labels (completed 2025-10-31)
  - GitHub: Created labels (epic, backend, android, documentation, testing) and applied to issues
  - GitLab: Created issue board "Reply AI Suggester Development Board" and matching labels
  - Acceptance criteria: Organized project structure with categorized issues and project boards.

- [x] Add README badges for project status (completed 2025-10-31)
  - Badges added: License (MIT), Python 3.8+, Android API 21+, Build Status, Codacy
  - Acceptance criteria: README displays professional badges with valid links.

## 7. Application Design & Architecture

- [ ] Design multi-agent orchestration system
  - Microgoals:
    - [ ] Define agent selection criteria (context analysis, user preferences, performance metrics)
    - [ ] Design agent combination strategies (parallel execution, sequential chaining, voting)
    - [ ] Create agent metadata schema (capabilities, cost, latency, quality scores)
  - Acceptance criteria: Design document in `docs/` with architecture diagrams and decision rationale.

- [ ] Design personalization and learning pipeline
  - Microgoals:
    - [ ] Define data collection points (typing patterns, suggestion acceptance rates, context analysis)
    - [ ] Design privacy-preserving data processing (local aggregation, differential privacy)
    - [ ] Create user consent and data control UX flows
  - Acceptance criteria: Privacy-by-design document with technical implementation plan.

- [ ] Design offline-first architecture
  - Microgoals:
    - [ ] Define offline capability boundaries (basic suggestions, cached responses, local models)
    - [ ] Design sync strategies (conflict resolution, data prioritization, bandwidth optimization)
    - [ ] Create offline UX patterns (degraded functionality indicators, sync status)
  - Acceptance criteria: Architecture document covering offline scenarios and user experience.

- [ ] Design performance and resource management
  - Microgoals:
    - [ ] Define performance budgets (response time, memory usage, battery impact)
    - [ ] Design caching strategies (suggestion caching, model caching, context caching)
    - [ ] Create resource monitoring and optimization triggers
  - Acceptance criteria: Performance requirements document with monitoring and optimization plans.

---

### Example of striking-out (do not remove lines)

~~- [ ] Old task that is superseded (superseded on 2025-10-31 by replan)~~

---

*File created: 2025-10-31*
*Last updated: 2025-10-31 - Added project management tasks, updated completion status, added design architecture section*
