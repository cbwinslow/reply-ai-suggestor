# Alibaba Cloud Qwen Provider

This directory contains the implementation of the Alibaba Cloud Qwen AI provider adapter for the Reply AI Suggester backend.

## Setup

### Prerequisites

1. **DashScope Account**: Sign up at [DashScope](https://dashscope.aliyun.com/)
2. **API Key**: Get your API key from the DashScope console
3. **Python Package**: Install the DashScope SDK

```bash
pip install dashscope
```

### Configuration

Set your API key as an environment variable:

```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

Or pass it directly in the provider configuration.

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | `"qwen-turbo"` | Model to use (qwen-turbo, qwen-plus, qwen-max) |
| `temperature` | float | `0.7` | Controls randomness (0.0-2.0) |
| `max_tokens` | int | `150` | Maximum tokens per response |
| `timeout_seconds` | int | `15` | Request timeout in seconds |

## Rate Limits

Rate limits vary by model and your DashScope plan:

- **Qwen-Turbo**: Up to 1000 requests/minute
- **Qwen-Plus**: Up to 500 requests/minute
- **Qwen-Max**: Up to 100 requests/minute

Check your DashScope dashboard for exact limits.

## Cost Estimates

Approximate costs per request (as of 2025):

- **Qwen-Turbo**: ~$0.0002 per 1K tokens
- **Qwen-Plus**: ~$0.0008 per 1K tokens
- **Qwen-Max**: ~$0.002 per 1K tokens

Typical suggestion request: ~$0.0003

## Usage Example

```python
from providers.qwen.provider import QwenProvider
from providers.base import ProviderConfig

config = ProviderConfig(
    api_key="your-dashscope-api-key",
    model_name="qwen-turbo",
    temperature=0.7
)

provider = QwenProvider(config)
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
cd backend/providers/qwen/tests
pytest test_integration.py
```

Tests use mocked responses and don't require a real API key.