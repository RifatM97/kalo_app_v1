"""
LLM Provider Factory
Selects and instantiates the appropriate LLM provider based on configuration
"""

import logging
from typing import Optional
from functools import lru_cache

from .base import LLMProvider, LLMConnectionError
from .llama_ollama import OllamaLlama3Provider
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm_provider(
    provider: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    ollama_base_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Typical usage:
        provider = get_llm_provider()  # Uses env vars
        response = await provider.generate_response(messages)
    
    Priority:
    1. Ollama (local, free, unlimited) - preferred if available
    2. OpenAI (cloud, requires API key)
    
    Args:
        provider: Force provider ("llama" or "openai"). If None, auto-detect.
        openai_api_key: OpenAI API key (uses env var if not provided)
        ollama_base_url: Ollama base URL (default: http://localhost:11434)
        ollama_model: Ollama model name (default: llama3)
    
    Returns:
        LLMProvider instance ready to use
        
    Raises:
        LLMConnectionError: If no provider is available
    """
    from app.config import settings
    
    # Use provided values or fall back to env vars/defaults
    provider_name = provider or getattr(settings, "LLM_PROVIDER", "llama").lower()
    openai_key = openai_api_key or getattr(settings, "OPENAI_API_KEY", None)
    ollama_url = ollama_base_url or getattr(
        settings, "OLLAMA_BASE_URL", "http://localhost:11434"
    )
    ollama_mdl = ollama_model or getattr(settings, "OLLAMA_MODEL", "llama3")
    
    # Forced provider
    if provider_name == "openai":
        logger.info("LLM Provider: OpenAI (forced)")
        if not openai_key:
            raise LLMConnectionError(
                "OpenAI provider selected but OPENAI_API_KEY not set"
            )
        text_model = getattr(settings, "OPENAI_MODEL_TEXT", "gpt-4o-mini")
        vision_model = getattr(settings, "OPENAI_MODEL_VISION", "gpt-4o")
        return OpenAIProvider(
            api_key=openai_key,
            text_model=text_model,
            vision_model=vision_model
        )
    
    elif provider_name == "llama":
        logger.info(f"LLM Provider: Ollama/{ollama_mdl}")
        return OllamaLlama3Provider(base_url=ollama_url, model=ollama_mdl)
    
    # Auto-detect (prefer Ollama if available, fall back to OpenAI)
    elif provider_name == "auto" or not provider_name:
        logger.info("LLM Provider: Auto-detecting...")
        
        # Try Ollama first
        try:
            ollama_provider = OllamaLlama3Provider(
                base_url=ollama_url, model=ollama_mdl
            )
            logger.info("✓ Ollama available, using as primary provider")
            return ollama_provider
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        
        # Fall back to OpenAI
        if openai_key:
            logger.info("✓ Falling back to OpenAI")
            text_model = getattr(settings, "OPENAI_MODEL_TEXT", "gpt-4o-mini")
            vision_model = getattr(settings, "OPENAI_MODEL_VISION", "gpt-4o")
            return OpenAIProvider(
                api_key=openai_key,
                text_model=text_model,
                vision_model=vision_model
            )
        
        # No provider available
        raise LLMConnectionError(
            "No LLM provider available. Install Ollama or set OPENAI_API_KEY."
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


async def check_llm_health() -> dict:
    """
    Check health of configured LLM provider.
    
    Returns:
        Dict with provider name and availability status
    """
    try:
        provider = get_llm_provider()
        is_available = await provider.is_available()
        
        return {
            "provider": provider.get_provider_name(),
            "available": is_available,
            "status": "healthy" if is_available else "unhealthy",
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {
            "provider": "unknown",
            "available": False,
            "status": "error",
            "error": str(e),
        }
