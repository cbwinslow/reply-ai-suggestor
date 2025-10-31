"""
Integration tests for Qwen provider adapter.

Tests the QwenProvider implementation with mocked DashScope API responses.
"""

import pytest
from unittest.mock import patch, MagicMock
from providers.qwen.provider import QwenProvider
from providers.base import ProviderConfig, SuggestRequest, ProviderAuthError, ProviderError


class TestQwenProvider:
    """Test suite for QwenProvider."""

    @pytest.fixture
    def valid_config(self):
        """Valid provider configuration."""
        return ProviderConfig(
            api_key="test-dashscope-key",
            model_name="qwen-turbo",
            temperature=0.7,
            max_tokens=150,
            timeout_seconds=15
        )

    @pytest.fixture
    def sample_request(self):
        """Sample suggestion request."""
        return SuggestRequest(
            context="Hello, how are you?",
            modes=["casual"],
            intensity=5,
            user_profile_summary="Friendly user who likes casual conversations"
        )

    def test_init_valid_config(self, valid_config):
        """Test provider initialization with valid config."""
        provider = QwenProvider(valid_config)
        assert provider.config.model_name == "qwen-turbo"
        assert abs(provider.config.temperature - 0.7) < 1e-6
        assert provider.config.max_tokens == 150

    def test_init_default_config(self):
        """Test provider initialization with minimal config."""
        config = ProviderConfig(api_key="test-key")
        provider = QwenProvider(config)
        assert provider.config.model_name == "qwen-turbo"
        assert abs(provider.config.temperature - 0.7) < 1e-6
        assert provider.config.max_tokens == 150

    def test_init_no_api_key(self):
        """Test provider initialization without API key."""
        config = ProviderConfig()
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ProviderAuthError):
                QwenProvider(config)

    def test_init_invalid_temperature(self):
        """Test provider initialization with invalid temperature."""
        config = ProviderConfig(api_key="test-key", temperature=3.0)
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            QwenProvider(config)

    def test_init_invalid_max_tokens(self):
        """Test provider initialization with invalid max tokens."""
        config = ProviderConfig(api_key="test-key", max_tokens=3000)
        with pytest.raises(ValueError, match="Max tokens must be between 1 and 2000"):
            QwenProvider(config)

    @patch('dashscope.Generation.call')
    def test_suggest_success(self, mock_call, valid_config, sample_request):
        """Test successful suggestion generation."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.output.text = '["Thanks!", "How are you?", "Nice to hear from you!"]'
        mock_response.usage = {"input_tokens": 50, "output_tokens": 30}
        mock_call.return_value = mock_response

        provider = QwenProvider(valid_config)
        response = provider.suggest(sample_request)

        assert len(response.suggestions) == 3
        assert "Thanks!" in response.suggestions
        assert response.metadata["provider"] == "qwen"
        assert response.metadata["model"] == "qwen-turbo"
        assert response.metadata["usage"] == {"input_tokens": 50, "output_tokens": 30}

        # Verify API call
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[1]["model"] == "qwen-turbo"
        assert abs(call_args[1]["temperature"] - 0.7) < 1e-6
        assert call_args[1]["max_tokens"] == 150
        assert len(call_args[1]["messages"]) == 2  # system + user

    @patch('dashscope.Generation.call')
    def test_suggest_json_parsing_fallback(self, mock_call, valid_config, sample_request):
        """Test suggestion generation with non-JSON response fallback."""
        # Mock response with plain text
        mock_response = MagicMock()
        mock_response.output.text = "1. Thanks for your message!\n2. That sounds great!\n3. Looking forward to it!"
        mock_call.return_value = mock_response

        provider = QwenProvider(valid_config)
        response = provider.suggest(sample_request)

        assert len(response.suggestions) == 3
        assert "Thanks for your message!" in response.suggestions

    @patch('dashscope.Generation.call')
    def test_suggest_response_parsing_error(self, mock_call, valid_config, sample_request):
        """Test suggestion generation with response parsing error."""
        # Mock response that causes parsing to fail
        mock_response = MagicMock()
        mock_response.output = None  # This will cause parsing to fail
        mock_call.return_value = mock_response

        provider = QwenProvider(valid_config)
        response = provider.suggest(sample_request)

        # Should return default suggestions
        assert len(response.suggestions) == 3
        assert "Thanks for your message!" in response.suggestions

    @patch('dashscope.Generation.call')
    def test_suggest_auth_error(self, mock_call, valid_config, sample_request):
        """Test suggestion generation with authentication error."""
        mock_call.side_effect = Exception("Invalid API key")

        provider = QwenProvider(valid_config)
        with pytest.raises(ProviderAuthError):
            provider.suggest(sample_request)

    @patch('dashscope.Generation.call')
    def test_suggest_rate_limit_error(self, mock_call, valid_config, sample_request):
        """Test suggestion generation with rate limit error."""
        mock_call.side_effect = Exception("Rate limit exceeded")

        provider = QwenProvider(valid_config)
        with pytest.raises(ProviderError) as exc_info:
            provider.suggest(sample_request)

        assert exc_info.value.retryable is True
        assert "quota exceeded" in str(exc_info.value).lower()

    @patch('dashscope.Generation.call')
    def test_suggest_generic_error(self, mock_call, valid_config, sample_request):
        """Test suggestion generation with generic error."""
        mock_call.side_effect = Exception("Network timeout")

        provider = QwenProvider(valid_config)
        with pytest.raises(ProviderError) as exc_info:
            provider.suggest(sample_request)

        assert exc_info.value.retryable is True
        assert "generation failed" in str(exc_info.value).lower()

    def test_build_messages_formal_mode(self, valid_config):
        """Test message building with formal mode."""
        config = ProviderConfig(api_key="test-key", model_name="qwen-turbo")
        provider = QwenProvider(config)

        request = SuggestRequest(
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
        config = ProviderConfig(api_key="test-key", model_name="qwen-turbo")
        provider = QwenProvider(config)

        request = SuggestRequest(
            context="Hey",
            modes=["casual"],
            intensity=8
        )

        messages = provider._build_messages(request)
        assert "casual, friendly language" in messages[0]["content"]
        assert "Be bold and creative" in messages[0]["content"]

    def test_build_messages_witty_mode(self, valid_config):
        """Test message building with witty mode."""
        config = ProviderConfig(api_key="test-key", model_name="qwen-turbo")
        provider = QwenProvider(config)

        request = SuggestRequest(
            context="Hi",
            modes=["witty"],
            intensity=2
        )

        messages = provider._build_messages(request)
        assert "Include humor and wit" in messages[0]["content"]
        assert "Be conservative and safe" in messages[0]["content"]

    def test_parse_response_valid_json(self, valid_config):
        """Test response parsing with valid JSON."""
        provider = QwenProvider(valid_config)

        mock_response = MagicMock()
        mock_response.output.text = '["Suggestion 1", "Suggestion 2", "Suggestion 3", "Suggestion 4"]'

        suggestions = provider._parse_response(mock_response)
        assert len(suggestions) == 3  # Should limit to 3
        assert suggestions == ["Suggestion 1", "Suggestion 2", "Suggestion 3"]

    def test_parse_response_plain_text(self, valid_config):
        """Test response parsing with plain text."""
        provider = QwenProvider(valid_config)

        mock_response = MagicMock()
        mock_response.output.text = "1. First suggestion\n2. Second suggestion\n3. Third suggestion"

        suggestions = provider._parse_response(mock_response)
        assert len(suggestions) == 3
        assert "First suggestion" in suggestions[0]

    def test_parse_response_empty(self, valid_config):
        """Test response parsing with empty response."""
        provider = QwenProvider(valid_config)

        mock_response = MagicMock()
        mock_response.output.text = ""

        suggestions = provider._parse_response(mock_response)
        # Should return defaults
        assert len(suggestions) == 3
        assert "Thanks for your message!" in suggestions[0]

    def test_get_provider_name(self, valid_config):
        """Test provider name retrieval."""
        provider = QwenProvider(valid_config)
        assert provider.get_provider_name() == "Alibaba Cloud Qwen"

    def test_get_cost_estimate(self, valid_config, sample_request):
        """Test cost estimation."""
        provider = QwenProvider(valid_config)
        cost = provider.get_cost_estimate(sample_request)
        assert abs(cost - 0.0003) < 1e-6