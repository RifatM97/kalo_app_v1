#!/usr/bin/env python3
"""
Test script for Kalo LLM providers and chatbot
Run this to verify setup and test both Ollama and OpenAI
"""

import asyncio
import sys
import json
from pathlib import Path

# Add kalo-backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_ollama():
    """Test Ollama provider"""
    print("\n" + "="*60)
    print("🦙 Testing Ollama Provider (Local Llama 3)")
    print("="*60)
    
    try:
        from app.services.llm.llama_ollama import OllamaLlama3Provider
        from app.services.llm.base import ChatMessage
        
        provider = OllamaLlama3Provider(
            base_url="http://localhost:11434",
            model="llama3"
        )
        
        # Check availability
        print("\n1. Checking if Ollama is available...")
        available = await provider.is_available()
        
        if not available:
            print("   ❌ Ollama not available (not running or wrong URL)")
            return False
        
        print("   ✓ Ollama is running and healthy")
        
        # Test generation
        print("\n2. Testing message generation...")
        messages = [
            ChatMessage(role="user", content="What is a healthy breakfast? Answer in 1-2 sentences.")
        ]
        
        response = await provider.generate_response(messages=messages, temperature=0.7)
        
        print(f"   ✓ Response received ({len(response.content)} chars)")
        print(f"\n   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Message: {response.content}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_openai():
    """Test OpenAI provider"""
    print("\n" + "="*60)
    print("🔑 Testing OpenAI Provider")
    print("="*60)
    
    try:
        from app.services.llm.openai_llm import OpenAIProvider
        from app.services.llm.base import ChatMessage
        from app.config import settings
        
        api_key = settings.OPENAI_API_KEY
        
        if not api_key or api_key.startswith("sk-proj-"):
            print("   ⚠️  No valid OpenAI API key in .env (expected for dev)")
            return None
        
        provider = OpenAIProvider(api_key=api_key, model="gpt-3.5-turbo")
        
        # Check availability
        print("\n1. Checking if OpenAI is available...")
        available = await provider.is_available()
        
        if not available:
            print("   ❌ OpenAI not available (check API key)")
            return False
        
        print("   ✓ OpenAI is configured")
        
        # Test generation
        print("\n2. Testing message generation...")
        messages = [
            ChatMessage(role="user", content="What is a healthy breakfast? Answer in 1-2 sentences.")
        ]
        
        response = await provider.generate_response(messages=messages, temperature=0.7)
        
        print(f"   ✓ Response received ({len(response.content)} chars)")
        print(f"\n   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Message: {response.content}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_factory():
    """Test LLM provider factory"""
    print("\n" + "="*60)
    print("🏭 Testing LLM Provider Factory")
    print("="*60)
    
    try:
        from app.services.llm.factory import get_llm_provider, check_llm_health
        
        print("\n1. Getting configured LLM provider...")
        provider = get_llm_provider()
        
        print(f"   ✓ Provider: {provider.get_provider_name()}")
        
        print("\n2. Checking LLM health...")
        health = await check_llm_health()
        
        print(f"   Provider: {health['provider']}")
        print(f"   Status: {health['status']}")
        print(f"   Available: {health['available']}")
        
        if not health['available']:
            print(f"   Error: {health.get('error')}")
            return False
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_chatbot():
    """Test chatbot service"""
    print("\n" + "="*60)
    print("💬 Testing Chatbot Service")
    print("="*60)
    
    try:
        from app.services.chatbot import (
            generate_chat_response,
            get_session_history,
            clear_session,
        )
        
        session_id = "test_session_123"
        
        print("\n1. Sending first message...")
        response1 = await generate_chat_response(
            message="What are the benefits of drinking water?",
            session_id=session_id,
        )
        
        print(f"   ✓ Response 1: {response1[:80]}...")
        
        print("\n2. Sending follow-up message (multi-turn)...")
        response2 = await generate_chat_response(
            message="How much water should I drink daily?",
            session_id=session_id,
        )
        
        print(f"   ✓ Response 2: {response2[:80]}...")
        
        print("\n3. Retrieving conversation history...")
        history = get_session_history(session_id)
        
        print(f"   ✓ Message count: {len(history)}")
        for msg in history:
            print(f"      - {msg['role']}: {msg['content'][:50]}...")
        
        print("\n4. Clearing session...")
        clear_session(session_id)
        
        history_after = get_session_history(session_id)
        
        if len(history_after) == 0:
            print("   ✓ Session cleared successfully")
            return True
        else:
            print(f"   ❌ Session not cleared (still has {len(history_after)} messages)")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 KALO LLM Provider Test Suite")
    print("="*60)
    
    results = {
        "ollama": None,
        "openai": None,
        "factory": None,
        "chatbot": None,
    }
    
    # Test factory first
    print("\n[Step 1/4] Testing LLM Provider Factory...")
    results["factory"] = await test_factory()
    
    # Only test specific providers if configured
    try:
        from app.config import settings
        
        if settings.LLM_PROVIDER.lower() in ["llama", "auto"]:
            print("\n[Step 2/4] Testing Ollama Provider...")
            results["ollama"] = await test_ollama()
        else:
            print("\n[Step 2/4] Skipping Ollama (not configured)")
        
        if settings.OPENAI_API_KEY:
            print("\n[Step 3/4] Testing OpenAI Provider...")
            results["openai"] = await test_openai()
        else:
            print("\n[Step 3/4] Skipping OpenAI (no API key)")
        
        print("\n[Step 4/4] Testing Chatbot Service...")
        results["chatbot"] = await test_chatbot()
    
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✓ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status:12} {name}")
    
    # Overall status
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print("\n" + "="*60)
    if passed == total and total > 0:
        print(f"✓ All {total} tests PASSED! 🎉")
        print("\nYour LLM provider is working correctly.")
        print("Test the API with:")
        print("  curl -X POST http://localhost:8000/api/ai/chat \\")
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"message": "Hello!"}\'')
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nCheck the output above for error details.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
