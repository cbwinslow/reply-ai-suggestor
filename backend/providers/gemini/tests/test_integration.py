"""
Integration tests for Gemini provider adapter.

These tests validate the Gemini provider's request/response handling
using mocked credentials and responses.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse, UsageMetadata

from ...base import ProviderConfig, SuggestRequest, ProviderAuthError
from ..gemini.provider import GeminiProvider


class TestGeminiProvider:
    """Test suite for Gemini provider."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock provider config."""
        return ProviderConfig(
            api_key="test-key",
            model_name="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=150,
            timeout_seconds=10
        )

    @pytest.fixture
    def sample_request(self):
        """Create a sample suggestion request."""
        return SuggestRequest(
            user_id="test-user",
            context="Thanks for the update on the project!",
            modes=["casual", "witty"],
            intensity=6
        )

    def test_config_validation_success(self, mock_config):
        """Test that valid config passes validation."""
        provider = GeminiProvider(mock_config)
        assert provider.get_provider_name() == "Google Gemini"
        assert provider.is_available()

    def test_config_validation_missing_api_key(self):
        """Test that missing API key fails validation."""
        config = ProviderConfig()  # No API key
        with patch.dict('os.environ', {}, clear=True):  # Clear env vars
            with pytest.raises(ProviderAuthError):
                GeminiProvider(config)

    def test_config_validation_invalid_temperature(self):
        """Test that invalid temperature fails validation."""
        config = ProviderConfig(
            api_key="test-key",
            temperature=3.0  # Invalid: > 2
        )
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            GeminiProvider(config)

    def test_config_validation_invalid_max_tokens(self):
        """Test that invalid max_tokens fails validation."""
        config = ProviderConfig(
            api_key="test-key",
            max_tokens=10000  # Invalid: > 8192
        )
        with pytest.raises(ValueError, match="Max tokens must be between 1 and 8192"):
            GeminiProvider(config)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_suggest_success(self, mock_model_class, mock_configure, mock_config, sample_request):
        """Test successful suggestion generation."""
        # Mock the model and response
        mock_model = Mock()
        mock_model_class.return_value = mock_model

        # Create mock response
        mock_response = Mock()
        mock_response.text = """Here are some suggestions:
1. Thanks! That sounds great - looking forward to seeing the results!
2. Awesome update, thanks for keeping me in the loop!
3. Sounds promising! Can't wait to hear more details."""

        # Mock usage metadata
        mock_response.usage_metadata = Mock()
        mock_response.usage_metadata.prompt_token_count = 50
        mock_response.usage_metadata.candidates_token_count = 75

        mock_model.generate_content.return_value = mock_response

        provider = GeminiProvider(mock_config)

        # Run the async test
        async def run_test():
            response = await provider.suggest(sample_request)

            # Verify response structure
            assert len(response.suggestions) == 3
            assert "Thanks!" in response.suggestions[0]
            assert "Awesome" in response.suggestions[1]
            assert "Sounds" in response.suggestions[2]

            # Verify metadata
            assert response.metadata["provider"] == "gemini"
            assert response.metadata["model"] == "gemini-1.5-flash"
            assert response.metadata["prompt_tokens"] == 50
            assert response.metadata["response_tokens"] == 75

        asyncio.run(run_test())

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_suggest_api_error(self, mock_model_class, mock_configure, mock_config, sample_request):
        """Test handling of API errors."""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("API quota exceeded")

        provider = GeminiProvider(mock_config)

        async def run_test():
            with pytest.raises(Exception, match="Gemini generation failed"):
                await provider.suggest(sample_request)

        asyncio.run(run_test())

    def test_cost_estimate(self, mock_config, sample_request):
        """Test cost estimation."""
        provider = GeminiProvider(mock_config)
        cost = provider.get_cost_estimate(sample_request)
        assert abs(cost - 0.0004) < 0.0001  # Gemini 1.5 Flash estimate, with tolerance

    def test_prompt_building(self, mock_config, sample_request):
        """Test that prompts are built correctly."""
        provider = GeminiProvider(mock_config)
        prompt = provider._build_prompt(sample_request)

        # Verify prompt contains key elements
        assert "Thanks for the update on the project!" in prompt
        assert "casual" in prompt
        assert "witty" in prompt
        assert "intensity guidance" in prompt
        assert "exactly 3 suggestions" in prompt

    def test_response_parsing(self, mock_config):
        """Test parsing of Gemini responses."""
        provider = GeminiProvider(mock_config)

        # Test normal response
        response_text = """1. Thanks for the update!
2. That sounds great!
3. Looking forward to it!"""

        suggestions = provider._parse_response(response_text)
        assert len(suggestions) == 3
        assert "Thanks for the update!" in suggestions[0]

        # Test response with fewer suggestions (should pad)
        short_response = "Just one suggestion here."
        suggestions = provider._parse_response(short_response)
        assert len(suggestions) == 3
        assert suggestions[0] == "Just one suggestion here."
        assert "Thanks for your message!" in suggestions[1]  # Default padding


if __name__ == "__main__":
    pytest.main([__file__])