# OpenRouter Provider

This directory contains the implementation of the OpenRouter AI provider adapter for the Reply AI Suggester backend.

OpenRouter provides access to various AI models through a unified OpenAI-compatible API, with many free models available for development and training.

## Setup

### Prerequisites

1. **OpenRouter Account**: Sign up at [OpenRouter](https://openrouter.ai/)
2. **API Key**: Get your API key from the OpenRouter dashboard
3. **Python Package**: Install the OpenAI SDK

```bash
pip install openai
```

### Configuration

Set your API key as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Or pass it directly in the provider configuration.

## Free Models for Development

OpenRouter offers many free models perfect for development and training:

| Model | Description | Context | Recommended |
|-------|-------------|---------|-------------|
| `qwen/qwen-2.5-14b-instruct:free` | Qwen 2.5 14B (High Quality) | 128K | ✅ Default |
| `google/gemma-7b-it:free` | Google's Gemma 7B | 8K | Good alternative |
| `meta-llama/llama-3.2-3b-instruct:free` | Meta's Llama 3.2 3B | 128K | Lightweight |
| `microsoft/wizardlm-2-8x22b:free` | Microsoft's WizardLM 2 | 128K | Creative tasks |
| `mistralai/mistral-7b-instruct:free` | Mistral's Mistral 7B | 32K | Balanced |

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | `"qwen/qwen-2.5-14b-instruct:free"` | Model to use (see available models) |
| `temperature` | float | `0.7` | Controls randomness (0.0-2.0) |
| `max_tokens` | int | `150` | Maximum tokens per response |
| `timeout_seconds` | int | `15` | Request timeout in seconds |

## Rate Limits

Rate limits vary by model and your OpenRouter plan:

- **Free Models**: Generous limits for development
- **Paid Models**: Higher limits based on credits purchased

Check your OpenRouter dashboard for exact limits.

## Cost Estimates

**Free Models**: $0.00 per request (perfect for development!)

**Paid Models** (when free quota exhausted):
- Varies by model ($0.001-$0.01 per request typically)
- Credits required for paid usage

## Usage Example

```python
from providers.openrouter.provider import OpenRouterProvider
from providers.base import ProviderConfig

config = ProviderConfig(
    api_key="your-openrouter-api-key",
    model_name="qwen/qwen-2.5-14b-instruct:free"  # High-quality free model
)

provider = OpenRouterProvider(config)
response = await provider.suggest(request)
```

## Error Handling

The provider handles common errors:

- **Authentication**: `ProviderAuthError` when API key is invalid
- **Rate Limits**: `ProviderError` with retryable=True for quota exceeded
- **Network Issues**: `ProviderError` with retryable=True for timeouts
- **Invalid Responses**: Graceful fallback to default suggestions

## Testing

Run the integration tests:

```bash
cd backend/providers/openrouter/tests
pytest test_integration.py
```

Tests use mocked responses and don't require a real API key.

## Model Selection for Development

For development and training, use these free models:

```python
# Best for general development (recommended default)
config.model_name = "qwen/qwen-2.5-14b-instruct:free"

# Good alternative with Google model
config.model_name = "google/gemma-7b-it:free"

# Lightweight and fast
config.model_name = "meta-llama/llama-3.2-3b-instruct:free"

# Creative and conversational
config.model_name = "microsoft/wizardlm-2-8x22b:free"
```