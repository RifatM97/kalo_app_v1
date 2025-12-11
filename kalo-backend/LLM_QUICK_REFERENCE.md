# 🚀 KALO LLM Integration - Quick Reference

## Installation (30 seconds)

### Step 1: Install Ollama
```bash
brew install ollama
ollama pull llama3
ollama serve  # Keep running in background
```

### Step 2: Update .env
```bash
LLM_PROVIDER=llama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Step 3: Start Backend
```bash
python -m uvicorn main:app --reload
```

---

## API Usage

### Send a Message
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many calories in an apple?"
  }'
```

**Response:**
```json
{
  "message": "A medium apple has about 95 calories...",
  "session_id": "session_abc123",
  "provider": "ollama/llama3"
}
```

### Multi-turn Conversation
```bash
# Message 1
curl -X POST http://localhost:8000/api/ai/chat \
  -d '{"message": "Tell me about protein", "session_id": "my_session"}'

# Message 2 (context preserved)
curl -X POST http://localhost:8000/api/ai/chat \
  -d '{"message": "How much should I eat daily?", "session_id": "my_session"}'
```

### Get Conversation History
```bash
curl http://localhost:8000/api/ai/chat/my_session/history
```

### Clear Session
```bash
curl -X POST http://localhost:8000/api/ai/chat/my_session/clear
```

---

## Code Usage (Python)

### One-off Response
```python
from app.services.chatbot import generate_single_response

response = await generate_single_response(
    message="What is a healthy breakfast?",
    temperature=0.7,
)
print(response)
```

### Multi-turn Chat
```python
from app.services.chatbot import generate_chat_response

# Message 1
resp1 = await generate_chat_response(
    message="Tell me about protein",
    session_id="my_session",
)

# Message 2
resp2 = await generate_chat_response(
    message="How much daily?",
    session_id="my_session",  # Same session
)
```

### Get Provider Info
```python
from app.services.llm import get_llm_provider

provider = get_llm_provider()
print(provider.get_provider_name())  # "ollama/llama3" or "openai/gpt-4"

is_healthy = await provider.is_available()
print(is_healthy)  # True or False
```

---

## Configuration

### Local Development (Ollama)
```bash
LLM_PROVIDER=llama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Cloud (OpenAI)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_KEY
LLM_MODEL=gpt-4o
```

### Smart Fallback (Try Ollama first)
```bash
LLM_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OPENAI_API_KEY=sk-proj-YOUR_KEY
LLM_MODEL=gpt-4o
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect to Ollama | Run: `ollama serve` |
| Ollama model not found | Run: `ollama pull llama3` |
| OpenAI quota exceeded | Switch to Ollama or check billing |
| Slow responses | Use `mistral` model or `gpt-3.5-turbo` |

---

## Architecture

```
App Code
    ↓
chatbot.generate_chat_response()
    ↓
llm.get_llm_provider()
    ↓
Ollama/OpenAI API
    ↓
JSON Response
```

---

## Files

| File | Purpose |
|------|---------|
| `app/services/llm/base.py` | Interface definition |
| `app/services/llm/llama_ollama.py` | Ollama client |
| `app/services/llm/openai_llm.py` | OpenAI client |
| `app/services/llm/factory.py` | Provider selection |
| `app/services/chatbot.py` | Chat service |
| `app/api/ai.py` | API endpoints |
| `app/config.py` | Configuration |
| `.env` | Environment variables |
| `LLM_SETUP_GUIDE.md` | Full setup guide |
| `test_llm_providers.py` | Test suite |

---

## Test Everything

```bash
python test_llm_providers.py
```

Expected: All tests pass ✅

---

## Need Help?

- **Setup**: See `LLM_SETUP_GUIDE.md`
- **Code**: Check docstrings in source files
- **Tests**: Run `test_llm_providers.py`
- **Examples**: Curl commands above

---

## Status

✅ **Ready to use**  
✅ **Production-ready**  
✅ **Fully documented**  
✅ **Tested**  

**Go ahead and start building!** 🎉
