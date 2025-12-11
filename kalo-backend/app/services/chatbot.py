"""
Chatbot Service
Provides unified interface for chat completions across different LLM providers
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime

from app.services.llm import ChatMessage, LLMResponse, get_llm_provider
from app.services.llm.base import LLMError

logger = logging.getLogger(__name__)


class ChatSession:
    """Manages a conversation session with message history"""
    
    def __init__(self, session_id: str, system_prompt: Optional[str] = None):
        """
        Initialize a chat session.
        
        Args:
            session_id: Unique session identifier
            system_prompt: Optional system prompt to guide the assistant
        """
        self.session_id = session_id
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str) -> ChatMessage:
        """Add a message to the session"""
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        self.last_activity = datetime.now()
        return msg
    
    def get_messages_for_api(self) -> List[ChatMessage]:
        """Get messages formatted for API call (includes system prompt)"""
        if not self.messages:
            return [ChatMessage(role="system", content=self.system_prompt)]
        
        # Always start with system prompt
        api_messages = [ChatMessage(role="system", content=self.system_prompt)]
        api_messages.extend(self.messages)
        return api_messages
    
    def clear(self):
        """Clear message history"""
        self.messages = []
        self.last_activity = datetime.now()


# Default system prompt for Kalo chatbot
DEFAULT_SYSTEM_PROMPT = """You are Kalo, a helpful AI assistant for a health and fitness app. You help users with:
- Nutritional advice and healthy recipes
- Fitness and workout recommendations
- Meal planning and grocery lists
- General wellness and health questions

Be friendly, concise, and informative. If asked about something outside your domain, politely redirect to health/fitness topics.
Keep responses to 2-3 sentences unless asked for more detail."""

# AI Coach system prompt for personalized training and nutrition coaching
AI_COACH_SYSTEM_PROMPT = """You are Kalo AI Coach, an expert fitness and nutrition coach. Your role is to provide personalized, actionable guidance.

EXPERTISE:
- Strength training, endurance, vertical jump, basketball performance
- Nutrition planning, macro tracking, meal timing
- Progressive overload, periodization, recovery strategies
- Form corrections, RPE guidance, injury prevention

COACHING STYLE:
- Give specific, actionable advice (sets, reps, RPE, weekly plans)
- Reference the user's training history and goals when available
- Be supportive and encouraging but honest
- Explain the "why" behind recommendations
- Keep responses concise (3-5 sentences) unless asked for detail

SAFETY:
- Always recommend consulting a doctor for pain, injuries, or medical concerns
- Never diagnose medical conditions
- Emphasize proper form and gradual progression

When given user context (goals, recent workouts, activity data), use it to personalize your advice."""


# In-memory session storage (use Redis in production)
_sessions: Dict[str, ChatSession] = {}


def get_or_create_session(session_id: str) -> ChatSession:
    """Get existing session or create a new one"""
    if session_id not in _sessions:
        logger.info(f"Creating new chat session: {session_id}")
        _sessions[session_id] = ChatSession(session_id)
    return _sessions[session_id]


async def generate_chat_response(
    message: str,
    session_id: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate a chat response using the configured LLM provider.
    
    This is the main entry point for the chatbot. It:
    1. Gets or creates a session
    2. Adds the user message
    3. Calls the LLM provider
    4. Stores the response
    5. Returns the response text
    
    Args:
        message: User's message/question
        session_id: Optional session ID for multi-turn conversations
                   If None, uses single-turn mode
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
    
    Returns:
        AI response text
        
    Raises:
        LLMError: If LLM generation fails
    """
    try:
        # Get or create session
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
        
        session = get_or_create_session(session_id)
        
        # Add user message
        session.add_message("user", message)
        logger.debug(f"User message added to session {session_id}: {message[:50]}...")
        
        # Get LLM provider
        provider = get_llm_provider()
        logger.debug(f"Using LLM provider: {provider.get_provider_name()}")
        
        # Get messages for API (includes system prompt)
        api_messages = session.get_messages_for_api()
        
        # Generate response
        logger.debug(f"Generating response from {provider.get_provider_name()}...")
        response: LLMResponse = await provider.generate_response(
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Store assistant response in session
        session.add_message("assistant", response.content)
        
        logger.info(
            f"✓ Response generated for session {session_id} "
            f"({provider.get_provider_name()}, {len(response.content)} chars)"
        )
        
        return response.content
    
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chatbot: {e}")
        raise LLMError(f"Chatbot error: {str(e)}")


async def generate_single_response(
    message: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate a single response without session history.
    
    Useful for one-off requests like recipe extraction structuring.
    
    Args:
        message: The message/prompt
        system_prompt: Custom system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens
    
    Returns:
        AI response text
    """
    try:
        provider = get_llm_provider()
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=message))
        
        # Generate response
        response: LLMResponse = await provider.generate_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.content
    
    except LLMError as e:
        logger.error(f"LLM error in single response: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise LLMError(f"Response generation error: {str(e)}")


def clear_session(session_id: str) -> bool:
    """
    Clear a chat session.
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        True if session was cleared, False if not found
    """
    if session_id in _sessions:
        logger.info(f"Clearing chat session: {session_id}")
        _sessions[session_id].clear()
        return True
    return False


def delete_session(session_id: str) -> bool:
    """
    Delete a chat session.
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        True if session was deleted, False if not found
    """
    if session_id in _sessions:
        logger.info(f"Deleting chat session: {session_id}")
        del _sessions[session_id]
        return True
    return False


def get_session_history(session_id: str) -> Optional[List[Dict]]:
    """
    Get message history for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        List of messages or None if session not found
    """
    if session_id in _sessions:
        session = _sessions[session_id]
        return [
            {
                "role": msg.role,
                "content": msg.content,
            }
            for msg in session.messages
        ]
    return None
