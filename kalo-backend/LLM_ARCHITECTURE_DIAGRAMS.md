# KALO LLM Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         iOS App / Web Client                    │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
                    HTTP POST /api/ai/chat
                    {"message": "Hello!"}
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │         FastAPI Application                 │
        │  (app/api/ai.py - Chat Endpoints)          │
        │  - POST /api/ai/chat                       │
        │  - GET  /api/ai/chat/{id}/history          │
        │  - POST /api/ai/chat/{id}/clear            │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │    Chatbot Service                          │
        │    (app/services/chatbot.py)                │
        │  ┌──────────────────────────────────┐      │
        │  │ generate_chat_response()         │      │
        │  │ - Session management             │      │
        │  │ - Message history                │      │
        │  │ - System prompts                 │      │
        │  └──────────┬───────────────────────┘      │
        │             │                              │
        │             ▼                              │
        │  get_llm_provider()                        │
        └────────────────────┬───────────────────────┘
                             │
        ┌────────────────────┴───────────────────────┐
        │    LLM Provider Factory                     │
        │    (app/services/llm/factory.py)           │
        │                                            │
        │  Configured via: LLM_PROVIDER env var      │
        └────┬──────────┬──────────┬────────────────┘
             │          │          │
      "llama"│   "openai"│  "auto" │
             │          │          │
    ┌────────▼───┐  ┌────▼────┐   │ Try Ollama
    │             │  │         │   │ then OpenAI
    ▼             │  ▼         ▼   │
 
 ┌──────────────────┐    ┌──────────────────┐
 │   Ollama/Llama   │    │   OpenAI API     │
 │   Provider       │    │   Provider       │
 │                  │    │                  │
 │ (llama_ollama    │    │ (openai_llm.py)  │
 │  .py)            │    │                  │
 │                  │    │                  │
 │ • Local HTTP API │    │ • Cloud API      │
 │ • Free/Unlimited │    │ • Requires key   │
 │ • Llama 3 model  │    │ • GPT-4o, etc.   │
 │ • Default        │    │ • Paid service   │
 └────────┬─────────┘    └──────┬───────────┘
          │                      │
          ▼                      ▼
   http://localhost:11434    https://api.openai.com

       ↓              ↓
    ┌──────────────────────────────────┐
    │    LLM Response                   │
    │    {                              │
    │      "content": "...",            │
    │      "model": "llama3/gpt-4o",    │
    │      "provider": "ollama/openai"  │
    │    }                              │
    └──────────────────┬────────────────┘
                       │
                       ▼
    HTTP 200 OK
    {
      "message": "...",
      "session_id": "session_xyz",
      "provider": "ollama/llama3"
    }
```

---

## Request/Response Flow

```
USER REQUEST
    │
    └─→ POST /api/ai/chat
           {
             "message": "What is protein?",
             "session_id": "session_123"
           }
                │
                ▼
        ┌──────────────────────────┐
        │ Validate Request         │
        │ - Check message not empty│
        │ - Generate/use session_id│
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │ Call generate_chat_response()
        │                          │
        │ 1. Get/create session    │
        │ 2. Store user message    │
        │ 3. Get LLM provider      │
        │ 4. Build message list    │
        │ 5. Call provider API     │
        │ 6. Store response        │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │ LLM Provider Selection   │
        │                          │
        │ if LLM_PROVIDER=="llama":
        │   → Ollama               │
        │ elif LLM_PROVIDER=="openai":
        │   → OpenAI               │
        │ elif LLM_PROVIDER=="auto":
        │   try Ollama             │
        │   → fallback OpenAI      │
        └──────────┬───────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │ Generate Response        │
        │                          │
        │ Provider async call:     │
        │ - Build HTTP request     │
        │ - Handle timeout         │
        │ - Parse response         │
        │ - Catch errors           │
        └──────────┬───────────────┘
                   │
                   ▼
    HTTP 200 OK ChatResponse
    {
      "message": "Protein is a macronutrient...",
      "session_id": "session_123",
      "provider": "ollama/llama3"
    }
```

---

## Provider Selection Logic

```
                    ┌─────────────────┐
                    │  get_llm_provider()
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Read config     │
                    │ LLM_PROVIDER    │
                    │ OPENAI_API_KEY  │
                    │ etc.            │
                    └────────┬────────┘
                             │
                    ┌────────▼────────────────────┐
                    │ Which provider selected?    │
                    └────┬──────┬──────┬──────────┘
                         │      │      │
                  "llama" │ "openai" │ "auto"
                         │      │      │
          ┌──────────────┘      │      └──────────────────┐
          │                     │                         │
          ▼                     ▼                         ▼
    ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐
    │ OllamaLlama  │  │ OpenAI Provider  │  │ Auto-detect:    │
    │ 3Provider    │  │                  │  │                 │
    │              │  │ if not API_KEY:  │  │ 1. Try Ollama   │
    │ Check config │  │   raise error    │  │    health       │
    │ - URL ok?    │  │ else:            │  │                 │
    │ - Model ok?  │  │   return provider│  │ 2. If fail:     │
    │              │  │                  │  │    Try OpenAI   │
    │ Return if ok │  │ Return provider  │  │    health       │
    │ else error   │  │                  │  │                 │
    └──────────────┘  └──────────────────┘  │ 3. Return best  │
                                             │    available    │
                                             │                 │
                                             │ 4. If both fail │
                                             │    raise error  │
                                             └─────────────────┘
```

---

## Multi-turn Conversation Flow

```
SESSION: session_abc123

TURN 1:
  User: "Tell me about protein"
  └─→ ChatSession.add_message("user", "...")
  └─→ Generate response
  └─→ ChatSession.add_message("assistant", "Protein is...")

TURN 2:
  User: "How much should I eat daily?"
  └─→ ChatSession.add_message("user", "...")
      Note: Session still has message from TURN 1
  └─→ Build message list for API:
      [
        {"role": "system", "content": "You are Kalo..."},
        {"role": "user", "content": "Tell me about protein"},
        {"role": "assistant", "content": "Protein is..."},
        {"role": "user", "content": "How much should I eat daily?"}
      ]
  └─→ Generate response (context aware!)
  └─→ ChatSession.add_message("assistant", "Most guidelines...")

TURN 3:
  User: "What about protein timing?"
  └─→ Same flow with full context
      All 5 messages sent to LLM
      Context preserved!

GET HISTORY:
  └─→ Return all 6 messages (3 user, 3 assistant)
```

---

## Configuration Cascade

```
                  ┌──────────────────┐
                  │  .env File       │
                  │                  │
                  │ LLM_PROVIDER     │
                  │ OLLAMA_BASE_URL  │
                  │ OLLAMA_MODEL     │
                  │ OPENAI_API_KEY   │
                  │ LLM_MODEL        │
                  └────────┬─────────┘
                           │
                    ┌──────▼──────┐
                    │  app/config │
                    │  .py         │
                    │  Settings    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────┐
                    │ factory.get_llm_    │
                    │ provider()           │
                    │                      │
                    │ Uses config values   │
                    │ to select provider   │
                    └──────┬──────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
    Ollama/Llama3                      OpenAI
    Provider                           Provider
```

---

## Error Handling Flow

```
                    try:
                      │
        ┌─────────────▼────────────┐
        │ Call LLM Provider API    │
        └─────────────┬────────────┘
                      │
    ┌─────────────────┴─────────────────┐
    │                                   │
    ▼                                   ▼
Success                           Exception
│                                 │
└─→ Parse response            ┌────▼─────────────┐
    Store in session           │ Check error type  │
    Return to client           └────┬─────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
           Connection          Quota/Rate         Timeout
           Error               Error              Error
           │                   │                  │
           ▼                   ▼                  ▼
      LLMConnection-       LLMQuota-          LLMTimeout-
      Error                Error              Error
      │                    │                  │
      └────────────────────┴──────────────────┘
                           │
                           ▼
                  Log error
                  Return 500 with
                  helpful message
                  to client
```

---

## Session Storage (Current & Future)

```
┌─ IN-MEMORY (Current - Dev Only) ──────────────┐
│                                               │
│ _sessions = {                                 │
│   "session_123": ChatSession(...),           │
│   "session_456": ChatSession(...),           │
│   ...                                        │
│ }                                            │
│                                              │
│ Pros: Simple, fast, no infrastructure       │
│ Cons: Lost on restart, doesn't scale        │
│                                              │
└──────────────────────────────────────────────┘

┌─ REDIS (Future - Production) ─────────────────┐
│                                               │
│ SET session:session_123 <json>                │
│ EXPIRE session:session_123 86400              │
│                                              │
│ GET session:session_123 → ChatSession         │
│                                              │
│ Pros: Persists, scales, fast                 │
│ Cons: Needs Redis infrastructure             │
│                                              │
└──────────────────────────────────────────────┘

┌─ DATABASE (Future - Data Analytics) ──────────┐
│                                               │
│ INSERT INTO chat_sessions ...                 │
│ INSERT INTO chat_messages ...                 │
│                                              │
│ Pros: Historical data, analytics             │
│ Cons: Slower, more complex                   │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Extension Points for Future Providers

```
To add a new LLM provider (e.g., Claude, Hugging Face):

1. Create new provider class
   ├─ Inherit from LLMProvider (base.py)
   ├─ Implement generate_response()
   ├─ Implement is_available()
   └─ Implement get_provider_name()

2. Update factory.py
   ├─ Import new provider
   ├─ Add to get_llm_provider() logic
   └─ Update auto-detection if needed

3. Update .env template
   ├─ Add new config variables
   └─ Update documentation

4. Add tests
   ├─ Test provider class
   ├─ Test factory selection
   └─ Test integration

No changes needed to:
  - chatbot.py (uses abstract interface)
  - api/ai.py (uses chatbot service)
  - app code (all agnostic to provider)
```

---

**All diagrams show the complete flow and architecture of the LLM system.**
