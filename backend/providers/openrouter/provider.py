"""
OpenRouter Provider Adapter

This module implements the OpenRouter AI provider adapter for the Reply AI Suggester.
OpenRouter provides access to various free and open-source AI models through a unified API.

Requirements:
- openai package (OpenRouter uses OpenAI-compatible API)
- OPENROUTER_API_KEY environment variable

Free Models Available (as of 2025):
- qwen/qwen-2.5-14b-instruct:free (Recommended - Qwen 2.5 14B)
- google/gemma-7b-it:free
- meta-llama/llama-3.2-3b-instruct:free
- microsoft/wizardlm-2-8x22b:free
- mistralai/mistral-7b-instruct:free

Cost Estimate:
- Free models: $0.00 per request
- Paid models: Varies by model (when free quota exhausted)
"""

import os
import json
from typing import List, Dict, Any
from openai import OpenAI

from ..base import BaseProvider, SuggestRequest, SuggestResponse, ProviderConfig, ProviderError, ProviderAuthError


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter AI provider implementation.

    Uses free/open-source models for cost-effective development and training.
    Falls back to paid models if free quota is exhausted.
    """

    def __init__(self, config: ProviderConfig):
        # Set default OpenRouter-specific config
        if config.model_name is None:
            config.model_name = "qwen/qwen-2.5-14b-instruct:free"
        if config.temperature is None:
            config.temperature = 0.7
        if config.max_tokens is None:
            config.max_tokens = 150
        if config.timeout_seconds is None:
            config.timeout_seconds = 15

        super().__init__(config)

        # Initialize OpenAI client with OpenRouter base URL
        api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ProviderAuthError("openrouter", "OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def _validate_config(self) -> None:
        """Validate OpenRouter-specific configuration."""
        if not self.config.api_key and not os.getenv("OPENROUTER_API_KEY"):
            raise ProviderAuthError("openrouter")

        if self.config.temperature < 0 or self.config.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

        if self.config.max_tokens < 1 or self.config.max_tokens > 2000:
            raise ValueError("Max tokens must be between 1 and 2000")

    async def suggest(self, request: SuggestRequest) -> SuggestResponse:
        """
        Generate reply suggestions using OpenRouter.

        Args:
            request: Suggestion request with context and parameters

        Returns:
            SuggestResponse with generated suggestions
        """
        try:
            # Build the messages for OpenRouter
            messages = self._build_messages(request)

            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout_seconds
            )

            # Extract suggestions from response
            suggestions = self._parse_response(response)

            # Build metadata
            metadata = {
                "provider": "openrouter",
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "usage": getattr(response, 'usage', None),
            }

            return SuggestResponse(
                suggestions=suggestions,
                metadata=metadata
            )

        except Exception as e:
            # Handle OpenRouter-specific errors
            error_str = str(e).lower()
            if "api" in error_str and "key" in error_str or "auth" in error_str or "unauthorized" in error_str:
                raise ProviderAuthError("openrouter") from e
            elif "quota" in error_str or "rate" in error_str or "limit" in error_str or "insufficient" in error_str:
                raise ProviderError(f"OpenRouter quota exceeded: {str(e)}", "openrouter", retryable=True) from e
            else:
                raise ProviderError(f"OpenRouter generation failed: {str(e)}", "openrouter", retryable=True) from e

    def _build_messages(self, request: SuggestRequest) -> List[Dict[str, str]]:
        """
        Build the messages array for OpenRouter based on the request parameters.

        Args:
            request: The suggestion request

        Returns:
            List of message dictionaries for OpenRouter API
        """
        # Determine style instructions based on modes
        style_instructions = []
        if "formal" in request.modes:
            style_instructions.append("Use formal, professional language")
        if "casual" in request.modes:
            style_instructions.append("Use casual, friendly language")
        if "witty" in request.modes:
            style_instructions.append("Include humor and wit")

        style_text = "; ".join(style_instructions) if style_instructions else "Use natural, conversational language"

        # Adjust intensity
        intensity_instruction = ""
        if request.intensity < 3:
            intensity_instruction = "Be conservative and safe with suggestions"
        elif request.intensity > 7:
            intensity_instruction = "Be bold and creative with suggestions"
        else:
            intensity_instruction = "Use balanced, appropriate suggestions"

        # Build the system message
        system_message = f"""You are a helpful assistant that generates reply suggestions.

Style instructions: {style_text}
Intensity guidance: {intensity_instruction}

Generate exactly 3 reply suggestions for the user's message.
Each suggestion should be a complete, natural reply under 100 characters.
Format your response as a JSON array of strings, like: ["suggestion 1", "suggestion 2", "suggestion 3"]"""

        # Build the user message
        user_message = f"Generate reply suggestions for this message: \"{request.context}\""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

    def _parse_response(self, response) -> List[str]:
        """
        Parse the OpenRouter response into a list of suggestions.

        Args:
            response: Raw response from OpenRouter API

        Returns:
            List of suggestion strings
        """
        try:
            # Extract content from response
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            else:
                content = str(response)

            # Try to parse as JSON first
            try:
                suggestions = json.loads(content.strip())
                if isinstance(suggestions, list):
                    return suggestions[:3]
            except json.JSONDecodeError:
                pass

            # Fallback: split by newlines and clean up
            suggestions = []
            for line in content.strip().split('\n'):
                line = line.strip()
                # Remove common prefixes
                line = line.lstrip('1234567890.- "')
                line = line.rstrip('"')
                if line and len(line) > 5:
                    suggestions.append(line)

            # Ensure we have exactly 3 suggestions
            while len(suggestions) < 3:
                suggestions.append("Thanks for your message!")

            return suggestions[:3]

        except Exception:
            # If parsing fails completely, return defaults
            return [
                "Thanks for your message!",
                "I appreciate the update.",
                "That sounds interesting."
            ]

    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "OpenRouter AI"

    def get_cost_estimate(self, request: SuggestRequest) -> float:
        """
        Estimate cost for OpenRouter request.

        OpenRouter free models: $0.00 per request
        Paid models vary by usage tier and model selected.

        For free models, always return 0.0
        """
        # Free models have no cost
        if ":free" in self.config.model_name:
            return 0.0

        # For paid models, rough estimate (varies by model)
        return 0.001  # Conservative estimate for paid models