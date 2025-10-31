"""
Gemini Provider Adapter

This module implements the Google Gemini AI provider adapter for the Reply AI Suggester.
It provides integration with Google's Gemini models for generating reply suggestions.

Requirements:
- google-generativeai package
- GEMINI_API_KEY environment variable

Rate Limits (as of 2025):
- Free tier: 60 requests/minute
- Paid tier: Higher limits based on billing

Cost Estimate:
- Gemini 1.5 Flash: ~$0.0004 per request (approximate)
"""

import os
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai.types import RequestOptions

from ..base import BaseProvider, SuggestRequest, SuggestResponse, ProviderConfig, ProviderError, ProviderAuthError


class GeminiProvider(BaseProvider):
    """
    Google Gemini AI provider implementation.

    Uses Gemini 1.5 Flash for fast, cost-effective suggestion generation.
    """

    def __init__(self, config: ProviderConfig):
        # Set default Gemini-specific config
        if config.model_name is None:
            config.model_name = "gemini-1.5-flash"
        if config.temperature is None:
            config.temperature = 0.7
        if config.max_tokens is None:
            config.max_tokens = 150
        if config.timeout_seconds is None:
            config.timeout_seconds = 10

        super().__init__(config)

        # Initialize Gemini client
        api_key = config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ProviderAuthError("gemini", "GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.model_name)

    def _validate_config(self) -> None:
        """Validate Gemini-specific configuration."""
        if not self.config.api_key and not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY must be provided via config or environment")

        if self.config.temperature < 0 or self.config.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")

        if self.config.max_tokens < 1 or self.config.max_tokens > 8192:
            raise ValueError("Max tokens must be between 1 and 8192")

    async def suggest(self, request: SuggestRequest) -> SuggestResponse:
        """
        Generate reply suggestions using Google Gemini.

        Args:
            request: Suggestion request with context and parameters

        Returns:
            SuggestResponse with generated suggestions
        """
        try:
            # Build the prompt based on request parameters
            prompt = self._build_prompt(request)

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                top_p=0.9,
                top_k=40,
            )

            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options=RequestOptions(timeout=self.config.timeout_seconds)
                )
            )

            # Extract suggestions from response
            suggestions = self._parse_response(response.text)

            # Build metadata
            metadata = {
                "provider": "gemini",
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', None),
                "response_tokens": getattr(response.usage_metadata, 'candidates_token_count', None),
            }

            return SuggestResponse(
                suggestions=suggestions,
                metadata=metadata
            )

        except Exception as e:
            # Handle Gemini-specific errors
            if "API_KEY" in str(e):
                raise ProviderAuthError("gemini") from e
            elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
                raise ProviderError(f"Gemini quota exceeded: {str(e)}", "gemini", retryable=True) from e
            else:
                raise ProviderError(f"Gemini generation failed: {str(e)}", "gemini", retryable=True) from e

    def _build_prompt(self, request: SuggestRequest) -> str:
        """
        Build the prompt for Gemini based on the request parameters.

        Args:
            request: The suggestion request

        Returns:
            Formatted prompt string
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

        # Build the complete prompt
        prompt = f"""Generate 3 reply suggestions for the following message context.

Context: "{request.context}"

Style instructions: {style_text}
Intensity guidance: {intensity_instruction}

Requirements:
- Each suggestion should be a complete, natural reply
- Suggestions should be appropriate for the context
- Provide exactly 3 suggestions, one per line
- Keep each suggestion under 100 characters
- Format: Just the suggestions, no numbering or extra text

Suggestions:"""

        return prompt

    def _parse_response(self, response_text: str) -> List[str]:
        """
        Parse the Gemini response into a list of suggestions.

        Args:
            response_text: Raw response from Gemini

        Returns:
            List of suggestion strings
        """
        # Split by newlines and clean up
        suggestions = []
        for line in response_text.strip().split('\n'):
            line = line.strip()
            # Remove common prefixes like "1.", "-", etc.
            line = line.lstrip('1234567890.-\s')
            if line and len(line) > 5:  # Filter out very short suggestions
                suggestions.append(line)

        # Ensure we have exactly 3 suggestions
        while len(suggestions) < 3:
            suggestions.append("Thanks for your message!")

        return suggestions[:3]

    def get_provider_name(self) -> str:
        """Return the provider name."""
        return "Google Gemini"

    def get_cost_estimate(self, request: SuggestRequest) -> float:
        """
        Estimate cost for Gemini request.

        Gemini 1.5 Flash pricing (approximate as of 2025):
        - Input: $0.00025 per 1K tokens
        - Output: $0.0005 per 1K tokens

        Rough estimate: ~$0.0004 per request
        """
        # Rough estimate based on typical usage
        return 0.0004