reply-ai-suggester — backend

This minimal FastAPI backend is a mock suggestion service used by the Android app during development.

Quick start

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app (development):

```bash
uvicorn backend.main:app --reload --port 8000
```

4. Example curl request:

```bash
curl -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u123", "context": "Hey, are we still on for tomorrow?", "modes": ["casual","formal","witty"], "intensity": 5}'
```

Notes

- `/suggest` returns mock suggestions. Replace with real model calls later.
- `/train` is a placeholder to accept training/personalization jobs.

Local test helper

Run `python backend/test_request.py` after starting the server to send a sample request and print the response.
