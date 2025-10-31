"""
Qwen Provider Adapter

This module implements the Alibaba Cloud Qwen AI provider adapter for the Reply AI Suggester.
It provides integration with Qwen models through the DashScope API.

Requirements:
- dashscope package
- DASHSCOPE_API_KEY environment variable

Rate Limits (as of 2025):
- Varies by model and tier
- Generally 100-1000 requests per minute

Cost Estimate:
- Qwen-Turbo: ~$0.0002 per 1K tokens
- Qwen-Plus: ~$0.0008 per 1K tokens
"""

import os
import json
from typing import List, Dict, Any
import dashscope
from dashscope import Generation

from ..base import BaseProvider, SuggestRequest, SuggestResponse, ProviderConfig, ProviderError, ProviderAuthError


class QwenProvider(BaseProvider):
    """
    Alibaba Cloud Qwen AI provider implementation.

    Uses Qwen-Turbo for cost-effective suggestion generation.
    """

    def __init__(self, config: ProviderConfig):
        # Set default Qwen-specific config
        if config.model_name is None:
            config.model_name = "qwen-turbo"
        if config.temperature is None:
            config.temperature = 0.7
        if config.max_tokens is None:
            config.max_tokens = 150
        if config.timeout_seconds is None:
            config.timeout_seconds = 15

        super().__init__(config)

        # Initialize DashScope client
        api_key = config.api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ProviderAuthError("qwen", "DASHSCOPE_API_KEY environment variable not set")

        dashscope.api_key = api_key

    def _validate_config(self) -> None:
        """Validate Qwen-specific configuration."""
        if not self.config.api_key and not os.getenv("DASHSCOPE_API_KEY"):
            raise ValueError("DASHSCOPE_API_KEY must be provided via config or environment")

        if self.config.temperature < 0 or self.config.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

        if self.config.max_tokens < 1 or self.config.max_tokens > 2000:
            raise ValueError("Max tokens must be between 1 and 2000")

    async def suggest(self, request: SuggestRequest) -> SuggestResponse:
        """
        Generate reply suggestions using Alibaba Cloud Qwen.

        Args:
            request: Suggestion request with context and parameters

        Returns:
            SuggestResponse with generated suggestions
        """
        try:
            # Build the messages for Qwen
            messages = self._build_messages(request)

            # Generate response
            response = Generation.call(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                result_format='message'  # Get structured response
            )

            # Extract suggestions from response
            suggestions = self._parse_response(response)

            # Build metadata
            metadata = {
                "provider": "qwen",
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
            # Handle Qwen-specific errors
            error_str = str(e).lower()
            if "api_key" in error_str or "auth" in error_str:
                raise ProviderAuthError("qwen") from e
            elif "quota" in error_str or "rate" in error_str or "limit" in error_str:
                raise ProviderError(f"Qwen quota exceeded: {str(e)}", "qwen", retryable=True) from e
            else:
                raise ProviderError(f"Qwen generation failed: {str(e)}", "qwen", retryable=True) from e

    def _build_messages(self, request: SuggestRequest) -> List[Dict[str, str]]:
        """
        Build the messages array for Qwen based on the request parameters.

        Args:
            request: The suggestion request

        Returns:
            List of message dictionaries for Qwen API
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
        Parse the Qwen response into a list of suggestions.

        Args:
            response: Raw response from Qwen API

        Returns:
            List of suggestion strings
        """
        try:
            # Extract content from response
            if hasattr(response, 'output') and hasattr(response.output, 'text'):
                content = response.output.text
            elif hasattr(response, 'output') and isinstance(response.output, dict):
                content = response.output.get('text', '')
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
                line = line.lstrip('1234567890.-\\s"')
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
        return "Alibaba Cloud Qwen"

    def get_cost_estimate(self, request: SuggestRequest) -> float:
        """
        Estimate cost for Qwen request.

        Qwen pricing (approximate as of 2025):
        - Qwen-Turbo: ~$0.0002 per 1K tokens
        - Qwen-Plus: ~$0.0008 per 1K tokens

        Rough estimate: ~$0.0003 per request
        """
        # Rough estimate based on typical usage
        return 0.0003