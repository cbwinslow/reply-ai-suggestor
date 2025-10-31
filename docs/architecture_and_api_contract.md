# Architecture and API Contract

## Architecture Overview

### Components:
1. **Android IME (Input Method Editor)**
   - Custom keyboard implemented using `InputMethodService`.
   - Suggestion strip UI built with Jetpack Compose.
   - Sends user input context to the backend `/suggest` endpoint.
   - Provides offline fallback suggestions using a local predictor.

2. **Backend**
   - FastAPI-based backend with a `/suggest` endpoint.
   - Integrates with AI provider adapters (OpenRouter, Gemini, Qwen).
   - Applies safety filters and redaction before returning suggestions.

3. **AI Provider Adapters**
   - Modular adapters for different AI models.
   - Handles communication with external AI services.

4. **Local Predictor**
   - Lightweight n-gram or template-based predictor for offline use.
   - Provides basic suggestions when the backend is unavailable.

### Data Flow:
1. User types text in the IME.
2. IME sends the context to the backend `/suggest` endpoint.
3. Backend fetches suggestions from AI providers or uses cached results.
4. Suggestions are returned to the IME and displayed in the suggestion strip.
5. User selects a suggestion, which is committed to the input field.

---

## API Contract

### `/suggest` Endpoint
- **Method**: POST
- **URL**: `/suggest`

#### Request Body
```json
{
  "context": "current typed text",
  "cursor_pos": 15,
  "style": "casual",
  "intensity": 3,
  "persona": "friendly",
  "client_id": "uuid",
  "timestamp": "2025-10-31T12:00:00Z"
}
```
- **context**: The text typed by the user.
- **cursor_pos**: Position of the cursor in the text.
- **style**: Desired tone of the suggestions (e.g., casual, formal).
- **intensity**: Level of verbosity (1-5).
- **persona**: Short text describing the desired personality.
- **client_id**: Unique identifier for the client.
- **timestamp**: ISO8601 timestamp of the request.

#### Response Body
```json
{
  "suggestions": [
    {"text": "Sure, that works!", "score": 0.9, "tokens": 12},
    {"text": "Okay, sounds good.", "score": 0.8, "tokens": 10},
    {"text": "Got it, thanks!", "score": 0.7, "tokens": 11}
  ],
  "model": "openrouter-dev",
  "cached": false
}
```
- **suggestions**: Array of suggestion objects.
  - **text**: Suggested text.
  - **score**: Confidence score of the suggestion.
  - **tokens**: Number of tokens used to generate the suggestion.
- **model**: Identifier for the AI model used.
- **cached**: Indicates if the response was served from cache.

#### Error Responses
- **429 Too Many Requests**: Rate limit exceeded.
- **503 Service Unavailable**: Backend is down.

---

## Caching and Offline Fallback
1. **Caching**:
   - Cache recent suggestions locally to reduce latency.
   - Use context hash as cache key.

2. **Offline Fallback**:
   - Use a local n-gram predictor or predefined templates.
   - Display an offline indicator in the suggestion strip.

---

## Next Steps
1. Implement the `/suggest` endpoint in the backend.
2. Scaffold the Android IME with a basic suggestion strip.
3. Integrate the backend with AI provider adapters.