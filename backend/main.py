from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging

app = FastAPI(title="reply-ai-suggester backend")

# Allow CORS for local development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reply-ai-suggester")


class SuggestRequest(BaseModel):
    user_id: str
    context: str
    modes: List[str] = ["casual", "formal", "witty"]
    intensity: int = 5


class SuggestResponse(BaseModel):
    suggestions: List[str]


@app.get("/health")
async def health():
    return {"status": "ok"}


def _intensity_suffix(intensity: int) -> str:
    # Simple heuristic: higher intensity -> add punctuation/emojis or stronger wording
    if intensity <= 0:
        return ""
    if intensity < 4:
        return ""  # subtle
    if intensity < 7:
        return "!"
    if intensity < 10:
        return "!! 😄"
    return "!!! 🔥"


@app.post("/suggest", response_model=SuggestResponse)
async def suggest(req: SuggestRequest, request: Request):
    logger.info("/suggest called by %s from %s", req.user_id, request.client)
    if not req.context or not req.context.strip():
        raise HTTPException(status_code=400, detail="Empty context")

    base = req.context.strip()
    suffix = _intensity_suffix(req.intensity)
    suggestions: List[str] = []

    for mode in req.modes:
        m = mode.lower()
        if m == "casual":
            suggestions.append(f"{base} — sounds good to me{suffix}")
        elif m == "formal":
            suggestions.append(f"{base}. I will proceed as discussed{suffix}")
        elif m == "witty":
            suggestions.append(f"{base} — because why not, right?{suffix}")
        else:
            # generic fallback
            suggestions.append(f"{base} ({m}){suffix}")

    # Limit suggestions to avoid very large responses
    suggestions = suggestions[:10]

    return SuggestResponse(suggestions=suggestions)


@app.post("/train")
async def train():
    # Placeholder for training/personalization endpoint
    logger.info("/train called (mock)")
    return {"status": "ok", "message": "training queued (mock)"}


# Simple in-memory personalization store for development/prototyping
_personalization_store = {}


@app.post("/upload_personalization")
async def upload_personalization(payload: dict):
    """Accepts JSON: {user_id: str, artifacts: dict}
    Stores artifacts in an in-memory store (mock). In production this should
    validate consent and write to encrypted storage or a secure DB.
    """
    user_id = payload.get("user_id")
    artifacts = payload.get("artifacts")
    if not user_id or artifacts is None:
        raise HTTPException(status_code=400, detail="user_id and artifacts required")
    _personalization_store[user_id] = {"artifacts": artifacts}
    logger.info("Saved personalization for %s (keys=%s)", user_id, list(artifacts.keys()) if isinstance(artifacts, dict) else [])
    return {"status": "ok"}


@app.post("/delete_personalization")
async def delete_personalization(payload: dict):
    """Accepts JSON: {user_id: str} and removes personalization data for the user."""
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    if user_id in _personalization_store:
        del _personalization_store[user_id]
        logger.info("Deleted personalization for %s", user_id)
        return {"status": "ok", "deleted": True}
    return {"status": "ok", "deleted": False}


@app.get("/personalization/{user_id}")
async def get_personalization(user_id: str):
    return _personalization_store.get(user_id, {})
