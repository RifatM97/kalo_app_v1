"""
Enhanced OpenAI Provider with Vision + JSON Support
Supports GPT-4 Vision for image analysis and structured JSON responses
"""

import logging
import base64
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base import (
    LLMProvider,
    ChatMessage,
    LLMResponse,
    LLMConnectionError,
    LLMQuotaError,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    Enhanced OpenAI provider with:
    - Text generation (chat)
    - Vision analysis (images)
    - Structured JSON responses
    - Multiple model support
    """
    
    def __init__(
        self,
        api_key: str,
        text_model: str = "gpt-4o-mini",  # Cheap for text
        vision_model: str = "gpt-4o",  # Vision capable
        organization: Optional[str] = None,
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            text_model: Model for text-only tasks (e.g. gpt-4o-mini)
            vision_model: Model for vision tasks (e.g. gpt-4o, gpt-4-turbo)
            organization: Optional organization ID
        """
        self.api_key = api_key
        self.text_model = text_model
        self.vision_model = vision_model
        self.organization = organization
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                organization=organization,
            )
            logger.info(f"✓ OpenAI initialized: text={text_model}, vision={vision_model}")
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
        Generate text response using OpenAI API.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with generated content
        """
        try:
            messages_list = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            kwargs = {
                "model": self.text_model,
                "messages": messages_list,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            logger.debug(f"OpenAI text request: {len(messages_list)} messages")
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            return LLMResponse(
                content=content,
                model=self.text_model,
                provider="openai",
                tokens_used=tokens_used,
            )
        
        except Exception as e:
            return self._handle_openai_error(e)
    
    async def generate_json_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Uses OpenAI's JSON mode to ensure valid JSON output.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Lower = more deterministic
            max_tokens: Maximum response tokens
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            LLMConnectionError: If API call fails
            ValueError: If response is not valid JSON
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            kwargs = {
                "model": self.text_model,
                "messages": messages,
                "temperature": temperature,
                "response_format": {"type": "json_object"},  # Force JSON
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            logger.debug(f"OpenAI JSON request: {prompt[:100]}...")
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"✓ JSON response: {tokens_used} tokens")
            
            # Parse JSON
            parsed = json.loads(content)
            return parsed
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            return self._handle_openai_error(e)
    
    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        max_tokens: Optional[int] = 4096,
    ) -> str:
        """
        Analyze image using GPT-4 Vision.
        
        Args:
            image_bytes: Image data as bytes
            prompt: Question/instruction about the image
            max_tokens: Maximum response tokens
            
        Returns:
            Text description/analysis
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # or "low" for faster/cheaper
                            }
                        }
                    ]
                }
            ]
            
            logger.debug(f"OpenAI Vision request: {len(image_bytes)} bytes")
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"✓ Vision analysis: {tokens_used} tokens")
            
            return content
        
        except Exception as e:
            return self._handle_openai_error(e)
    
    async def analyze_image_json(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = 4096,
    ) -> Dict[str, Any]:
        """
        Analyze image and return structured JSON.
        
        Combines vision with JSON mode for structured recipe extraction.
        
        Args:
            image_bytes: Image data
            prompt: Instruction (should mention JSON format)
            system_prompt: Optional system context
            max_tokens: Maximum response tokens
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            })
            
            logger.debug(f"OpenAI Vision+JSON request: {len(image_bytes)} bytes")
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"✓ Vision+JSON: {tokens_used} tokens")
            
            parsed = json.loads(content)
            return parsed
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from vision response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            return self._handle_openai_error(e)
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is configured and accessible."""
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return False
        
        # Quick validation: check if key format is valid
        if not self.api_key.startswith("sk-"):
            logger.warning("OpenAI API key has invalid format")
            return False
        
        logger.info(f"✓ OpenAI available: {self.text_model} + {self.vision_model}")
        return True
    
    def get_provider_name(self) -> str:
        """Return provider name."""
        return f"openai/{self.text_model}"
    
    def _handle_openai_error(self, error: Exception):
        """Centralized error handling for OpenAI API calls."""
        error_str = str(error)
        
        # Quota/billing errors
        if "429" in error_str or "quota" in error_str.lower():
            logger.error(f"OpenAI quota exceeded: {error_str}")
            raise LLMQuotaError(
                "OpenAI quota exceeded. Check billing: "
                "https://platform.openai.com/account/billing"
            )
        
        # Authentication errors
        elif "401" in error_str or "unauthorized" in error_str.lower():
            logger.error(f"OpenAI authentication failed: {error_str}")
            raise LLMConnectionError("Invalid OpenAI API key")
        
        # Invalid request
        elif "400" in error_str or "invalid" in error_str.lower():
            logger.error(f"OpenAI invalid request: {error_str}")
            raise LLMConnectionError(f"Invalid request: {error_str}")
        
        # Generic error
        else:
            logger.error(f"OpenAI API error: {error_str}")
            raise LLMConnectionError(f"OpenAI error: {error_str}")
