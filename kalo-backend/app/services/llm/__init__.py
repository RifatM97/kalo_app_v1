"""
LLM Provider abstraction layer
Supports multiple LLM backends: Ollama (Llama 3), OpenAI, etc.
"""

from .base import LLMProvider, ChatMessage, LLMResponse
from .factory import get_llm_provider

__all__ = [
    "LLMProvider",
    "ChatMessage",
    "LLMResponse",
    "get_llm_provider",
]
