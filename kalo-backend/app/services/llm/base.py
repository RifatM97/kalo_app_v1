"""
Base LLM Provider interface
All LLM implementations must inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message with role and content"""
    role: str  # "user", "assistant", "system"
    content: str


class LLMResponse(BaseModel):
    """Response from LLM provider"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    provider: str


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    Implementations should provide:
    - Single-turn chat completion
    - Multi-turn conversation support (optional)
    - Error handling and retry logic
    """
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate a response based on messages.
        
        Args:
            messages: List of ChatMessage objects
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with the generated content
            
        Raises:
            LLMError: If generation fails
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if this provider is available and healthy.
        
        Returns:
            True if provider is ready to use, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name (e.g., 'ollama', 'openai')"""
        pass


class LLMError(Exception):
    """Base exception for LLM provider errors"""
    pass


class LLMConnectionError(LLMError):
    """Raised when unable to connect to LLM provider"""
    pass


class LLMQuotaError(LLMError):
    """Raised when LLM provider quota is exceeded"""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM provider request times out"""
    pass
