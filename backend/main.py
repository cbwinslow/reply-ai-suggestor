from typing import List
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.config import settings

app = FastAPI(title=settings.app_name + " backend")

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(settings.app_name)


class SuggestRequest(BaseModel):
    user_id: str
    context: str
    modes: List[str] = ["casual", "formal", "witty"]
    intensity: int = 5
    provider: str = "mock"


class SuggestionItem(BaseModel):
    text: str
    tone: str


class SuggestResponse(BaseModel):
    suggestions: List[SuggestionItem]


@app.get("/health")
async def health():
    return {"status": "ok"}


from backend.providers.base import BaseProvider, SuggestRequest as BaseSuggestRequest, SuggestResponse, SuggestionItem, ProviderConfig

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


class MockProvider(BaseProvider):
    def _validate_config(self):
        pass

    async def suggest(self, request: BaseSuggestRequest) -> SuggestResponse:
        base = request.context.strip()
        suffix = _intensity_suffix(request.intensity)
        suggestions: List[SuggestionItem] = []

        for mode in request.modes:
            m = mode.lower()
            if m == "casual":
                suggestions.append(SuggestionItem(text=f"{base} — sounds good to me{suffix}", tone="casual"))
            elif m == "formal":
                suggestions.append(SuggestionItem(text=f"{base}. I will proceed as discussed{suffix}", tone="formal"))
            elif m == "witty":
                suggestions.append(SuggestionItem(text=f"{base} — because why not, right?{suffix}", tone="witty"))
            else:
                suggestions.append(SuggestionItem(text=f"{base} ({m}){suffix}", tone="neutral"))

        suggestions = suggestions[:10]
        return SuggestResponse(suggestions=suggestions)

    def get_provider_name(self) -> str:
        return "Mock Provider"

    def get_cost_estimate(self, request: BaseSuggestRequest) -> float:
        return 0.0
providers = {
    "mock": MockProvider(ProviderConfig()),
}


@app.post("/suggest", response_model=SuggestResponse)
async def suggest(req: SuggestRequest, request: Request):
    logger.info("/suggest called by %s from %s", req.user_id, request.client)
    if not req.context or not req.context.strip():
        raise HTTPException(status_code=400, detail="Empty context")

    provider = providers.get(req.provider, providers["mock"])
    base_request = BaseSuggestRequest(
        user_id=req.user_id,
        context=req.context,
        modes=req.modes,
        intensity=req.intensity
    )
    response = await provider.suggest(base_request)
    return response


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
    keys_info = list(artifacts.keys()) if isinstance(artifacts, dict) else []
    logger.info("Saved personalization for %s (keys=%s)", user_id, keys_info)
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
