"""
Llama 3 via Ollama - Local LLM Provider
Requires: ollama running locally at http://localhost:11434
Model: llama3 (can be pulled via `ollama pull llama3`)
"""

import asyncio
import aiohttp
import logging
from typing import List, Optional

from .base import (
    LLMProvider,
    ChatMessage,
    LLMResponse,
    LLMConnectionError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)


class OllamaLlama3Provider(LLMProvider):
    """Llama 3 via Ollama HTTP API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
        timeout: int = 60,
    ):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use (default: llama3)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.logger = logger
    
    async def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate response using Ollama API.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Max tokens (ignored for Ollama, kept for compatibility)
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            LLMConnectionError: If can't connect to Ollama
            LLMTimeoutError: If request times out
        """
        try:
            # Convert messages to Ollama format
            messages_list = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            payload = {
                "model": self.model,
                "messages": messages_list,
                "temperature": temperature,
                "stream": False,
            }
            
            url = f"{self.base_url}/api/chat"
            
            self.logger.debug(f"Calling Ollama: {url} with model {self.model}")
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            self.logger.error(
                                f"Ollama error ({response.status}): {error_text}"
                            )
                            raise LLMConnectionError(
                                f"Ollama returned {response.status}: {error_text}"
                            )
                        
                        data = await response.json()
                        content = data.get("message", {}).get("content", "")
                        
                        if not content:
                            self.logger.warning("Ollama returned empty content")
                            content = "I couldn't generate a response. Please try again."
                        
                        return LLMResponse(
                            content=content,
                            model=self.model,
                            provider="ollama",
                            tokens_used=None,  # Ollama doesn't return token count
                        )
                
                except asyncio.TimeoutError:
                    self.logger.error(f"Ollama request timed out ({self.timeout}s)")
                    raise LLMTimeoutError(
                        f"Ollama request timed out after {self.timeout} seconds"
                    )
                except aiohttp.ClientConnectionError as e:
                    self.logger.error(f"Failed to connect to Ollama: {e}")
                    raise LLMConnectionError(
                        f"Cannot connect to Ollama at {self.base_url}. "
                        "Make sure Ollama is running: `ollama serve`"
                    )
        
        except (LLMConnectionError, LLMTimeoutError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in Ollama provider: {e}")
            raise LLMConnectionError(f"Ollama provider error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Ollama is running and responsive.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        model_names = [m.get("name") for m in models]
                        
                        if self.model in model_names:
                            self.logger.info(
                                f"✓ Ollama available with {self.model} model"
                            )
                            return True
                        else:
                            self.logger.warning(
                                f"Model {self.model} not found. Available: {model_names}"
                            )
                            return False
        
        except Exception as e:
            self.logger.debug(f"Ollama not available: {e}")
            return False
    
    def get_provider_name(self) -> str:
        """Return provider name"""
        return f"ollama/{self.model}"
