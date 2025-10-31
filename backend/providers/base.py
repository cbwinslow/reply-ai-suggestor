"""
Provider Adapter Interface

This module defines the base interface for AI provider adapters used by the Reply AI Suggester backend.
All provider implementations must inherit from BaseProvider and implement the suggest() method.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class SuggestRequest(BaseModel):
    """Request model for suggestion generation."""
    user_id: str
    context: str
    modes: List[str]  # e.g., ["casual", "formal", "witty"]
    intensity: int  # 0-10 scale
    user_profile_summary: Optional[str] = None


class SuggestResponse(BaseModel):
    """Response model for suggestion generation."""
    suggestions: List[str]
    metadata: Optional[Dict[str, Any]] = None


class ProviderConfig(BaseModel):
    """Configuration model for provider settings."""
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None


class BaseProvider(ABC):
    """
    Abstract base class for AI provider adapters.

    All provider implementations must:
    1. Inherit from this class
    2. Implement the suggest() method
    3. Handle their own configuration and error handling
    4. Follow the SuggestRequest/SuggestResponse contract
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider with configuration.

        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the provider configuration.
        Raise ValueError if configuration is invalid.
        """
        pass

    @abstractmethod
    async def suggest(self, request: SuggestRequest) -> SuggestResponse:
        """
        Generate reply suggestions based on the request.

        Args:
            request: Suggestion request with context and parameters

        Returns:
            SuggestResponse with generated suggestions and optional metadata

        Raises:
            ProviderError: If the provider fails to generate suggestions
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the human-readable name of this provider."""
        pass

    @abstractmethod
    def get_cost_estimate(self, request: SuggestRequest) -> float:
        """
        Estimate the cost of processing this request in USD.

        Args:
            request: The request to estimate cost for

        Returns:
            Estimated cost in USD (0.0 if free or unknown)
        """
        pass

    def is_available(self) -> bool:
        """
        Check if this provider is currently available for use.

        Returns:
            True if provider can be used, False otherwise
        """
        try:
            self._validate_config()
            return True
        except Exception:
            return False


class ProviderError(Exception):
    """Base exception for provider-related errors."""

    def __init__(self, message: str, provider_name: str, retryable: bool = False):
        super().__init__(message)
        self.provider_name = provider_name
        self.retryable = retryable


class ProviderRateLimitError(ProviderError):
    """Exception raised when provider rate limits are exceeded."""

    def __init__(self, provider_name: str, retry_after_seconds: Optional[int] = None):
        message = f"Rate limit exceeded for provider {provider_name}"
        if retry_after_seconds:
            message += f". Retry after {retry_after_seconds} seconds"
        super().__init__(message, provider_name, retryable=True)
        self.retry_after_seconds = retry_after_seconds


class ProviderAuthError(ProviderError):
    """Exception raised when provider authentication fails."""

    def __init__(self, provider_name: str):
        message = f"Authentication failed for provider {provider_name}"
        super().__init__(message, provider_name, retryable=False)