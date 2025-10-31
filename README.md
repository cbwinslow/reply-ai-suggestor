# reply-ai-suggester

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Android API 21+](https://img.shields.io/badge/Android-21+-green.svg)](https://developer.android.com/studio)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/cbwinslow/reply-ai-suggestor/actions)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1234567890abcdef)](https://www.codacy.com/gh/cbwinslow/reply-ai-suggestor/dashboard)

Reply AI Suggester is a prototype scaffold for an Android application that provides AI-driven reply suggestions directly from the user's typing surface (keyboard / IME overlay). The goal is a low-friction, privacy-first assistant that suggests replies in multiple styles and intensities and can be personalized per-user.

This repository contains:
- `android/` — Kotlin + Jetpack Compose Android app skeleton, IME prototype, settings screen, and a simple networking client.
- `backend/` — FastAPI mock backend with `/suggest`, `/train` and `/health` endpoints to prototype model integration and personalization flows.
- `docs/` — roadmap, privacy checklist and design notes.
- `agents.md`, `gemini.md`, `qwen.md`, `project_summary.md`, `vscode.md` — new documentation files that describe agent design, model tradeoffs, and developer setup.

Important repository governance
--------------------------------
This repository follows an append-only documentation policy to preserve auditability and historical context.

- Do NOT edit or delete documentation files (including `agents.md`, `gemini.md`, `qwen.md`, `SRS.md`, `docs/*`) without explicit written approval from a project approver. The only exceptions are:
	- Appending new entries to `tasks.md` or journal-style files.
	- Adding new documents that do not modify existing documents in-place.
- To deprecate or replace text, strike through the original and append the updated content with a short rationale and date.

See `tasks.md` (root) for the append-only project task list and `CONTRIBUTING.md` for the PR/approval process.

Summary of current progress (short)
- Project scaffold completed: Android skeleton, backend mock server, docs and privacy notes.
- Backend enhanced: CORS, /health, intensity-aware mock suggestions, logging.
- Android networking implemented: `NetworkClient.kt` posts to backend, wired into Compose UI.
- IME prototype: `KeyboardStubService` registered, `res/xml/method.xml` added so the app can be enabled as a keyboard for manual testing.

Important design & safety notes
- Privacy-first: default to local processing and explicit opt-in before uploading messages for personalization. Prefer InputMethodService (custom keyboard) to reduce permission friction.
- Play Store: IME vs Accessibility has policy implications. Plan for a clear privacy policy and justification if any sensitive permissions are required.

Quick start (backend)

1. Create and activate a Python virtual environment (project root):

```bash
cd /home/foomanchu8008/apps/reply-ai-suggestor
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Run the backend locally (development):

```bash
uvicorn backend.main:app --port 8000
```

3. Optional: run the test helper to POST a sample request to the server:

```bash
python backend/test_request.py
```

Running the Android app locally

- Open the `android/` folder in Android Studio and allow Gradle to sync. The module build files are minimal placeholders — Android Studio will prompt to finish plugin and Gradle wrapper configuration.
- Run the app on an emulator. The networking client uses `10.0.2.2:8000` which maps the Android emulator to the host `localhost`. If you run on a device, update `NetworkClient.SUGGEST_URL` to your host's LAN address.

Files you should review first
- `backend/main.py` — mock endpoints and request handling
- `android/app/src/main/java/com/replyaisuggester/MainActivity.kt` — Compose UI + networking call
- `android/app/src/main/java/com/replyaisuggester/NetworkClient.kt` — HttpURLConnection helper
- `android/app/src/main/java/com/replyaisuggester/KeyboardStubService.kt` — IME prototype

Where we go from here — the plan (detailed)

See `project_summary.md` for the full plan. High level:

1) Finalize requirements & constraints (policy, consent, supported API levels). Target: decide Android minSdk and whether to target only IME integration or add overlay mode.
2) Implement secure personalization pipeline: opt-in UX, encryption-at-rest, selective uploading with explicit user preview, and deletion/export endpoints.
3) Integrate a production-grade model: evaluate hosted LLM (Gemini, Qwen, OpenAI) vs on-device models (Llama2 variants). Add a provider abstraction and implement a prototype using a hosted API.
4) Improve Android client: robust IME (Compose-based keyboard), coroutines + OkHttp networking, settings persistence, and Play Billing integration for tiers.
5) Testing & compliance: unit/UI tests, Play Store policy review, privacy audit.

If you want me to continue, pick a next step (recommended):
- Implement the secure personalization data flow (consent UI + local encrypted store) or
- Replace the NetworkClient with OkHttp + coroutines and wire the backend host into settings; or
- Prototype a full IME UI that surfaces suggestions inline and can commit selected suggestions into the input field.

Thanks — full documentation files were added (`agents.md`, `project_summary.md`, `gemini.md`, `qwen.md`, `vscode.md`) as requested; open them to review the detailed analysis and plans.
