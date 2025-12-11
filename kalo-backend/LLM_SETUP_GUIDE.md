# 🤖 KALO LLM Provider Setup Guide

This guide explains how to set up and use the new pluggable LLM provider system in Kalo.

## Quick Start

### Option 1: Ollama (Local - Recommended for Development)

**Free, unlimited, runs locally, no API key needed.**

#### Step 1: Install Ollama
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

#### Step 2: Pull Llama 3 Model
```bash
ollama pull llama3
```

#### Step 3: Start Ollama Server
```bash
ollama serve
```

This starts Ollama on `http://localhost:11434` (default).

#### Step 4: Configure Kalo Backend
```bash
# In .env, set:
LLM_PROVIDER=llama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

#### Step 5: Test
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a healthy breakfast?"}'
```

**That's it!** Kalo will now use local Llama 3.

---

### Option 2: OpenAI (Cloud)

**Requires API key, has usage quotas, costs money.**

#### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api/keys
2. Create a new API key
3. Copy it

#### Step 2: Configure Kalo Backend
```bash
# In .env, set:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
LLM_MODEL=gpt-4o  # or gpt-3.5-turbo, gpt-4, etc.
```

#### Step 3: Test
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a healthy breakfast?"}'
```

---

### Option 3: Auto (Smart Fallback)

**Tries Ollama first, falls back to OpenAI if unavailable.**

```bash
# In .env, set:
LLM_PROVIDER=auto
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE  # Still required as fallback
```

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `llama` | Which provider to use: `llama`, `openai`, `auto` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |
| `OPENAI_API_KEY` | (none) | OpenAI API key |
| `LLM_MODEL` | `gpt-4o` | OpenAI model name |

### Example .env Files

**Development (Ollama)**
```bash
LLM_PROVIDER=llama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

**Production (OpenAI)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_KEY
LLM_MODEL=gpt-4o
```

**Fallback (Try Ollama, use OpenAI if unavailable)**
```bash
LLM_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OPENAI_API_KEY=sk-proj-YOUR_KEY
LLM_MODEL=gpt-4o
```

---

## API Usage

### Chat Endpoint

**Single-turn question:**
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many calories in a banana?"
  }'
```

Response:
```json
{
  "message": "A medium banana has about 105 calories and is rich in potassium...",
  "session_id": "session_abc123def",
  "provider": "ollama/llama3"
}
```

**Multi-turn conversation (same session):**
```bash
# First message
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about protein",
    "session_id": "session_abc123def"
  }'

# Follow-up in same conversation
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much protein should I eat daily?",
    "session_id": "session_abc123def"
  }'
```

### Chat History

**Get conversation history:**
```bash
curl http://localhost:8000/api/ai/chat/session_abc123def/history
```

Response:
```json
{
  "session_id": "session_abc123def",
  "messages": [
    {"role": "user", "content": "Tell me about protein"},
    {"role": "assistant", "content": "Protein is a macronutrient..."},
    {"role": "user", "content": "How much should I eat daily?"},
    {"role": "assistant", "content": "Most guidelines recommend..."}
  ],
  "message_count": 4
}
```

**Clear session:**
```bash
curl -X POST http://localhost:8000/api/ai/chat/session_abc123def/clear
```

---

## Troubleshooting

### Error: "Cannot connect to Ollama at http://localhost:11434"

**Solution:** Make sure Ollama is running:
```bash
# In a new terminal:
ollama serve

# Or check if it's running:
curl http://localhost:11434/api/tags
```

### Error: "Model llama3 not found"

**Solution:** Pull the model:
```bash
ollama pull llama3

# List available models:
ollama list
```

### Error: "OpenAI API key not set"

**Solution:** Set your API key in `.env`:
```bash
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
LLM_PROVIDER=openai
```

### Error: "insufficient_quota" (OpenAI)

**Solution:** Your OpenAI account has hit usage limits:
1. Go to https://platform.openai.com/account/billing/overview
2. Check your usage and limits
3. Add payment method or request quota increase
4. Alternatively, switch to Ollama (free, local):
   ```bash
   LLM_PROVIDER=llama
   ```

### Error: "Model gpt-4o not available"

**Solution:** Check your OpenAI account access. You may need to:
1. Switch to `gpt-3.5-turbo` (always available):
   ```bash
   LLM_MODEL=gpt-3.5-turbo
   ```
2. Or request GPT-4 access at https://platform.openai.com

### Slow responses from Ollama

**Possible causes:**
- Model is running on CPU (slow). Use a faster model like `mistral`:
  ```bash
  ollama pull mistral
  OLLAMA_MODEL=mistral
  ```
- System RAM is low. Close other applications.
- First run takes longer (model loading). Subsequent requests are faster.

---

## Advanced: Adding New LLM Providers

To add a new provider (e.g., Claude, Hugging Face, local model):

1. Create `app/services/llm/YOUR_PROVIDER.py`:
```python
from .base import LLMProvider, ChatMessage, LLMResponse

class YourProvider(LLMProvider):
    async def generate_response(self, messages: List[ChatMessage], **kwargs) -> LLMResponse:
        # Your implementation here
        pass
    
    async def is_available(self) -> bool:
        # Check if provider is ready
        pass
    
    def get_provider_name(self) -> str:
        return "your-provider"
```

2. Update `app/services/llm/factory.py`:
```python
from .your_provider import YourProvider

def get_llm_provider(...):
    if provider_name == "your-provider":
        return YourProvider(...)
```

3. Update `.env`:
```bash
LLM_PROVIDER=your-provider
```

---

## Performance Notes

| Provider | Speed | Cost | Setup | Quota |
|----------|-------|------|-------|-------|
| **Ollama (Llama 3)** | 🟡 Medium | Free | Easy | Unlimited |
| **Ollama (Mistral)** | 🟢 Fast | Free | Easy | Unlimited |
| **OpenAI (GPT-3.5)** | 🟢 Fast | $ | Easy | Limited |
| **OpenAI (GPT-4o)** | 🟡 Medium | $$ | Easy | Limited |

**Recommendation:**
- **Development/Testing**: Use Ollama (free, local, no quota)
- **Production**: Use OpenAI (faster, more capable) or Ollama (cost-effective at scale)

---

## Related Files

- **LLM Abstraction**: `app/services/llm/`
- **Chatbot Service**: `app/services/chatbot.py`
- **Configuration**: `app/config.py`
- **API Endpoints**: `app/api/ai.py`

---

**Questions?** Check the troubleshooting section above or review the docstrings in the source files.
