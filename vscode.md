# VS Code development notes

This document contains tips to develop and debug the Reply AI Suggester project in VS Code.

Workspace

- Open the repository root (`/home/foomanchu8008/apps/reply-ai-suggestor`) in VS Code.
- Use the Python extension for backend development and the Kotlin/Android extensions for Android work (or open the `android/` module in Android Studio for full Android support).

Extensions recommended

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Kotlin (fwcd.kotlin)
- Android iOS Support (redhat.ansible for some tasks) — Android Studio remains the recommended IDE for building/running emulators.
- GitLens (eamodio.gitlens)

Running the backend in the VS Code terminal

1. Create and activate virtualenv in the workspace root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Run the server (no reload recommended if file watch limits are hit):

```bash
uvicorn backend.main:app --port 8000
```

Debugging

- Use VS Code's Python debug config to run `backend.main` with `uvicorn.run` or attach to a running process.
- For quick checks, `python backend/test_request.py` hits the local server.

Android

- Open the `android/` folder in Android Studio to run and debug the app on emulators or connected devices.
- If you prefer to stay in VS Code, you can edit Kotlin source there, but running/emulating an Android device and Gradle sync should happen in Android Studio.

Notes about file watchers

- On some Linux systems, the OS limit for file watches may be low; uvicorn `--reload` uses file watchers. If you see `OS file watch limit reached`, either:
  - start uvicorn without `--reload`, or
  - increase the inotify watches limit (`sudo sysctl fs.inotify.max_user_watches=524288`) for development machines.

Codacy / Analysis

- The repo includes Codacy instructions in `.github/instructions/codacy.instructions.md`. When you edit files, the project policy may require running Codacy CLI analysis. See that file for guidance.

Developer checklist

- Keep personal data out of commits (use test-only or sanitized data).
- Add unit tests for backend endpoints when you change behavior.
- Use the `backend/test_request.py` helper for quick server validation.
