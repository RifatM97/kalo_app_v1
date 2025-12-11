"""
OpenAI LLM Provider
Supports GPT-3.5, GPT-4, GPT-4o, etc.
"""

import logging
from typing import List, Optional

from .base import (
    LLMProvider,
    ChatMessage,
    LLMResponse,
    LLMConnectionError,
    LLMQuotaError,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        organization: Optional[str] = None,
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-3.5-turbo, gpt-4, gpt-4o, etc.)
            organization: Optional organization ID
        """
        self.api_key = api_key
        self.model = model
        self.organization = organization
        self.logger = logger
        
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                organization=organization,
            )
        except ImportError:
            raise ImportError(
                "OpenAI client not installed. Run: pip install openai"
            )
    
    async def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate response using OpenAI API.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            LLMQuotaError: If quota exceeded
            LLMConnectionError: If API call fails
        """
        try:
            # Convert messages to OpenAI format
            messages_list = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages_list,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            self.logger.debug(
                f"Calling OpenAI: model={self.model}, "
                f"messages={len(messages_list)}"
            )
            
            # Use client.chat.completions (new API v1.0.0+)
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider="openai",
                tokens_used=tokens_used,
            )
        
        except Exception as e:
            error_str = str(e)
            
            # Check for specific errors
            if "429" in error_str or "quota" in error_str.lower():
                self.logger.error(f"OpenAI quota exceeded: {error_str}")
                raise LLMQuotaError(
                    "OpenAI quota exceeded. Check billing: "
                    "https://platform.openai.com/account/billing/overview"
                )
            elif "401" in error_str or "unauthorized" in error_str.lower():
                self.logger.error(f"OpenAI authentication failed: {error_str}")
                raise LLMConnectionError(f"OpenAI auth failed: Invalid API key")
            else:
                self.logger.error(f"OpenAI API error: {error_str}")
                raise LLMConnectionError(f"OpenAI API error: {error_str}")
    
    async def is_available(self) -> bool:
        """
        Check if OpenAI API is available.
        
        Note: We can't reliably check without making a request (which costs money),
        so we just check if the API key is set.
        
        Returns:
            True if API key is configured, False otherwise
        """
        if not self.api_key:
            self.logger.warning("OpenAI API key not configured")
            return False
        
        self.logger.info(f"✓ OpenAI available with {self.model} model")
        return True
    
    def get_provider_name(self) -> str:
        """Return provider name"""
        return f"openai/{self.model}"
