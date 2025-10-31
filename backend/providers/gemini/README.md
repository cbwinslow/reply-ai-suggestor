# Gemini Provider

This directory contains the Google Gemini AI provider adapter for the Reply AI Suggester backend.

## Setup

1. Install the required package:
```bash
pip install google-generativeai
```

2. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Set the environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Configuration

The Gemini provider supports the following configuration options:

- `api_key`: Your Gemini API key (can also use GEMINI_API_KEY env var)
- `model_name`: Model to use (default: "gemini-1.5-flash")
- `temperature`: Creativity level 0-2 (default: 0.7)
- `max_tokens`: Maximum response length (default: 150)
- `timeout_seconds`: Request timeout (default: 10)

## Rate Limits

- **Free tier**: 60 requests per minute
- **Paid tier**: Higher limits based on your billing plan

## Cost Estimate

- **Gemini 1.5 Flash**: ~$0.0004 per request
- **Gemini 1.5 Pro**: ~$0.00125 per request

Monitor your usage in the [Google Cloud Console](https://console.cloud.google.com/).

## Usage Example

```python
from backend.providers.gemini.provider import GeminiProvider
from backend.providers.base import ProviderConfig, SuggestRequest

config = ProviderConfig(
    api_key="your-key",
    model_name="gemini-1.5-flash"
)

provider = GeminiProvider(config)
request = SuggestRequest(
    user_id="user123",
    context="Thanks for the update!",
    modes=["casual", "witty"],
    intensity=6
)

response = await provider.suggest(request)
print(response.suggestions)
```

## Error Handling

The provider handles common Gemini errors:
- `ProviderAuthError`: Invalid API key
- `ProviderError`: Rate limits, network issues, or API errors

## Testing

Run the integration test:
```bash
python -m pytest backend/providers/gemini/tests/test_integration.py
```

*Last updated: 2025-10-31*