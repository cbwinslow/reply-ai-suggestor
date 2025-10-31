"""
Integration tests for OpenRouter provider adapter.

Tests the OpenRouterProvider implementation with mocked OpenAI API responses.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

from providers.openrouter.provider import OpenRouterProvider
from providers.base import ProviderConfig, SuggestRequest, ProviderAuthError, ProviderError


class TestOpenRouterProvider:
    """Test suite for OpenRouterProvider."""

    @pytest.fixture
    def valid_config(self):
        """Valid provider configuration."""
        return ProviderConfig(
            api_key="test-openrouter-key",
            model_name="qwen/qwen-2.5-14b-instruct:free",
            temperature=0.7,
            max_tokens=150,
            timeout_seconds=15
        )

    @pytest.fixture
    def sample_request(self):
        """Sample suggestion request."""
        return SuggestRequest(
            user_id="test-user-123",
            context="Hello, how are you?",
            modes=["casual"],
            intensity=5,
            user_profile_summary="Friendly user who likes casual conversations"
        )

    def test_init_valid_config(self, valid_config):
        """Test provider initialization with valid config."""
        provider = OpenRouterProvider(valid_config)
        assert provider.config.model_name == "qwen/qwen-2.5-14b-instruct:free"
        assert abs(provider.config.temperature - 0.7) < 1e-6
        assert provider.config.max_tokens == 150

    def test_init_default_config(self):
        """Test provider initialization with minimal config."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        assert provider.config.model_name == "qwen/qwen-2.5-14b-instruct:free"
        assert abs(provider.config.temperature - 0.7) < 1e-6
        assert provider.config.max_tokens == 150

    def test_init_no_api_key(self):
        """Test provider initialization without API key."""
        config = ProviderConfig()
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ProviderAuthError):
                OpenRouterProvider(config)

    def test_init_invalid_temperature(self):
        """Test provider initialization with invalid temperature."""
        config = ProviderConfig(api_key="test-key", temperature=3.0)
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            OpenRouterProvider(config)

    def test_init_invalid_max_tokens(self):
        """Test provider initialization with invalid max tokens."""
        config = ProviderConfig(api_key="test-key", max_tokens=3000)
        with pytest.raises(ValueError, match="Max tokens must be between 1 and 2000"):
            OpenRouterProvider(config)

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_success(self, mock_openai_class, valid_config, sample_request):
        """Test successful suggestion generation."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["Thanks!", "How are you?", "Nice to hear from you!"]'
        mock_response.usage = {"prompt_tokens": 50, "completion_tokens": 30}
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenRouterProvider(valid_config)
        response = asyncio.run(provider.suggest(sample_request))

        assert len(response.suggestions) == 3
        assert "Thanks!" in response.suggestions
        assert response.metadata["provider"] == "openrouter"
        assert response.metadata["model"] == "qwen/qwen-2.5-14b-instruct:free"
        assert response.metadata["usage"] == {"prompt_tokens": 50, "completion_tokens": 30}

        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "qwen/qwen-2.5-14b-instruct:free"
        assert abs(call_args[1]["temperature"] - 0.7) < 1e-6
        assert call_args[1]["max_tokens"] == 150
        assert len(call_args[1]["messages"]) == 2  # system + user

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_json_parsing_fallback(self, mock_openai_class, valid_config, sample_request):
        """Test suggestion generation with non-JSON response fallback."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1. Thanks for your message!\n2. That sounds great!\n3. Looking forward to it!"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenRouterProvider(valid_config)
        response = asyncio.run(provider.suggest(sample_request))

        assert len(response.suggestions) == 3
        assert "Thanks for your message!" in response.suggestions

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_response_parsing_error(self, mock_openai_class, valid_config, sample_request):
        """Test suggestion generation with response parsing error."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = []  # This will cause parsing to fail
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenRouterProvider(valid_config)
        response = asyncio.run(provider.suggest(sample_request))

        # Should return default suggestions
        assert len(response.suggestions) == 3
        assert "Thanks for your message!" in response.suggestions

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_auth_error(self, mock_openai_class, valid_config, sample_request):
        """Test suggestion generation with authentication error."""
        # Mock the OpenAI client to raise auth error
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Invalid API key")

        provider = OpenRouterProvider(valid_config)
        with pytest.raises(ProviderAuthError):
            asyncio.run(provider.suggest(sample_request))

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_rate_limit_error(self, mock_openai_class, valid_config, sample_request):
        """Test suggestion generation with rate limit error."""
        # Mock the OpenAI client to raise quota error
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

        provider = OpenRouterProvider(valid_config)
        with pytest.raises(ProviderError) as exc_info:
            asyncio.run(provider.suggest(sample_request))

        assert exc_info.value.retryable is True
        assert "quota exceeded" in str(exc_info.value).lower()

    @patch('providers.openrouter.provider.OpenAI')
    def test_suggest_generic_error(self, mock_openai_class, valid_config, sample_request):
        """Test suggestion generation with generic error."""
        # Mock the OpenAI client to raise generic error
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Network timeout")

        provider = OpenRouterProvider(valid_config)
        with pytest.raises(ProviderError) as exc_info:
            asyncio.run(provider.suggest(sample_request))

        assert exc_info.value.retryable is True
        assert "generation failed" in str(exc_info.value).lower()

    def test_build_messages_formal_mode(self, valid_config):
        """Test message building with formal mode."""
        config = ProviderConfig(api_key="test-key", model_name="qwen/qwen-2.5-14b-instruct:free")
        provider = OpenRouterProvider(config)

        request = SuggestRequest(
            user_id="test-user-123",
            context="Hello",
            modes=["formal"],
            intensity=5
        )

        messages = provider._build_messages(request)
        assert len(messages) == 2
        assert "formal, professional language" in messages[0]["content"]
        assert "Generate reply suggestions for this message: \"Hello\"" == messages[1]["content"]

    def test_build_messages_casual_mode(self, valid_config):
        """Test message building with casual mode."""
        config = ProviderConfig(api_key="test-key", model_name="qwen/qwen-2.5-14b-instruct:free")
        provider = OpenRouterProvider(config)

        request = SuggestRequest(
            user_id="test-user-123",
            context="Hey",
            modes=["casual"],
            intensity=8
        )

        messages = provider._build_messages(request)
        assert "casual, friendly language" in messages[0]["content"]
        assert "Be bold and creative" in messages[0]["content"]

    def test_build_messages_witty_mode(self, valid_config):
        """Test message building with witty mode."""
        config = ProviderConfig(api_key="test-key", model_name="qwen/qwen-2.5-14b-instruct:free")
        provider = OpenRouterProvider(config)

        request = SuggestRequest(
            user_id="test-user-123",
            context="Hi",
            modes=["witty"],
            intensity=2
        )

        messages = provider._build_messages(request)
        assert "Include humor and wit" in messages[0]["content"]
        assert "Be conservative and safe" in messages[0]["content"]

    def test_parse_response_valid_json(self, valid_config):
        """Test response parsing with valid JSON."""
        provider = OpenRouterProvider(valid_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["Suggestion 1", "Suggestion 2", "Suggestion 3", "Suggestion 4"]'

        suggestions = provider._parse_response(mock_response)
        assert len(suggestions) == 3  # Should limit to 3
        assert suggestions == ["Suggestion 1", "Suggestion 2", "Suggestion 3"]

    def test_parse_response_plain_text(self, valid_config):
        """Test response parsing with plain text."""
        provider = OpenRouterProvider(valid_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1. First suggestion\n2. Second suggestion\n3. Third suggestion"

        suggestions = provider._parse_response(mock_response)
        assert len(suggestions) == 3
        assert "First suggestion" in suggestions[0]

    def test_parse_response_empty(self, valid_config):
        """Test response parsing with empty response."""
        provider = OpenRouterProvider(valid_config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""

        suggestions = provider._parse_response(mock_response)
        # Should return defaults
        assert len(suggestions) == 3
        assert "Thanks for your message!" in suggestions[0]

    def test_get_provider_name(self, valid_config):
        """Test provider name retrieval."""
        provider = OpenRouterProvider(valid_config)
        assert provider.get_provider_name() == "OpenRouter AI"

    def test_get_cost_estimate_free_model(self, valid_config, sample_request):
        """Test cost estimation for free models."""
        provider = OpenRouterProvider(valid_config)
        cost = provider.get_cost_estimate(sample_request)
        assert abs(cost - 0.0) < 1e-6

    def test_get_cost_estimate_paid_model(self):
        """Test cost estimation for paid models."""
        config = ProviderConfig(api_key="test-key", model_name="anthropic/claude-3-haiku")
        provider = OpenRouterProvider(config)
        cost = provider.get_cost_estimate(SuggestRequest(
            user_id="test-user-123",
            context="test",
            modes=["casual"],
            intensity=5
        ))
        assert abs(cost - 0.001) < 1e-6