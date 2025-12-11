# 🚀 KALO Backend - AI Recipe Extraction Pipeline

> Extract recipes from TikTok, Instagram, and YouTube videos using AI vision and language models.

## ✨ Features

- 🎥 **Multi-platform video support** (TikTok, Instagram, YouTube)
- 🖼️ **Frame extraction** from videos
- 📝 **OCR text detection** using PaddleOCR
- 🔍 **Food detection** using YOLOv8
- 🎙️ **Audio transcription** using OpenAI Whisper
- 🧠 **Recipe structuring** using GPT-4o
- ⚡ **Async task processing** with Celery + Redis
- 📱 **iOS-compatible JSON responses**
- 🐳 **Docker support** with docker-compose

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI (Python 3.9+) |
| **Video Download** | yt-dlp |
| **Frame Extraction** | OpenCV |
| **OCR** | PaddleOCR |
| **Object Detection** | YOLOv8 |
| **Audio** | OpenAI Whisper |
| **LLM** | OpenAI GPT-4o |
| **Task Queue** | Celery + Redis |
| **Database** | PostgreSQL |
| **Deployment** | Docker + Docker Compose |

## 📋 Requirements

- Python 3.9+
- Redis (for Celery)
- PostgreSQL (optional, for persistence)
- OpenAI API key with sufficient quota
- FFmpeg (optional, for audio extraction)

## 🚀 Quick Start

### 1. **Setup Environment**

```bash
cd /Users/rifathossain/Desktop/kalo/kalo-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. **Start Services**

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start FastAPI Backend
python -m uvicorn main:app --reload

# Terminal 3: Start Celery Worker
celery -A app.celery_app worker -l info
```

### 3. **Test It**

```bash
# Health check
curl http://localhost:8000/health

# Start recipe extraction
curl -X POST http://localhost:8000/api/ai/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/shorts/dQw4w9WgXcQ"}'

# Check status
curl http://localhost:8000/api/ai/extract-recipe/TASK_ID/status
```

### 4. **Using Docker**

```bash
# Build and start all services
export OPENAI_API_KEY="sk-proj-YOUR_KEY"
docker-compose up

# Access at http://localhost:8000
```

## 📚 API Documentation

### **Extract Recipe** (Async)

```
POST /api/ai/extract-recipe
Content-Type: application/json

Request:
{
  "url": "https://www.youtube.com/shorts/dQw4w9WgXcQ"
}

Response (202):
{
  "task_id": "a1b2c3d4e5f6",
  "status": "processing",
  "title": null
}
```

### **Check Status**

```
GET /api/ai/extract-recipe/{task_id}/status

Response (200):
{
  "task_id": "a1b2c3d4e5f6",
  "status": "completed|processing|failed",
  "title": "Delicious Pasta",
  "ingredients": [
    {"name": "Pasta", "quantity": 400, "unit": "g"},
    {"name": "Olive Oil", "quantity": 2, "unit": "tbsp"}
  ],
  "steps": [
    {"step": 1, "instruction": "Boil water"}
  ],
  "macros": {
    "calories": 450,
    "protein": 16,
    "carbs": 68,
    "fat": 12
  }
}
```

## 📁 Project Structure

```
kalo-backend/
├── app/
│   ├── ai/
│   │   ├── recipe_extractor.py       # Main pipeline
│   │   ├── meal_planner.py
│   │   ├── workout_generator.py
│   │   └── insights_engine.py
│   ├── api/
│   │   ├── ai.py                     # Recipe endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── ...
│   ├── db/
│   ├── celery_app.py                 # Celery config
│   ├── tasks.py                      # Async tasks
│   └── config.py
├── debug_pipeline.py                  # Debugging script
├── test_pipeline_real.py              # Integration tests
├── main.py                            # Entry point
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env                               # Configuration
└── README.md
```

## 🔧 Configuration

### **Environment Variables** (`.env`)

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_KEY
LLM_MODEL=gpt-4o

# AI Models
WHISPER_MODEL=base
FOOD_DETECTION_MODEL=yolov8n

# Redis
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/kalo

# JWT
SECRET_KEY=your-secret-key-here
```

## 🐛 Troubleshooting

### **Error: OPENAI_API_KEY not set**
```bash
# Make sure .env file exists with valid key
export OPENAI_API_KEY="sk-proj-YOUR_KEY"
```

### **Error: Error code 429 - insufficient_quota**
- Your OpenAI account has hit usage limits
- Visit https://platform.openai.com/account/billing/overview
- Add payment method or increase quota

### **Error: Redis connection failed**
```bash
# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### **Error: ffmpeg not found**
- Audio extraction is optional
- Install: `brew install ffmpeg` (macOS)
- Or: `apt-get install ffmpeg` (Linux)

### **Error: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Pipeline Stages

### **1. Video Download** (30-60s)
- Uses `yt-dlp` to download from various sources
- Supports TikTok, Instagram, YouTube
- Downloads best available quality
- File saved to temp directory

### **2. Frame Extraction** (10-30s)
- Uses OpenCV to extract frames
- Samples every 30 frames (reduces load)
- Saves as JPEG files
- ~10 frames typically used for analysis

### **3. Audio Extraction** (5-10s)
- Uses FFmpeg to extract audio
- Converts to WAV format
- 16kHz sample rate
- Optional (gracefully skipped if FFmpeg missing)

### **4. Transcription** (30-90s)
- Uses OpenAI Whisper
- Converts speech to text
- English language
- Optional if audio extraction failed

### **5. OCR** (20-60s)
- Uses PaddleOCR
- Extracts visible text from frames
- Filters low-confidence results
- Processes ~10 sampled frames

### **6. Object Detection** (10-30s)
- Uses YOLOv8 model
- Detects objects in frames
- Identifies food items
- Returns class names with confidence

### **7. Recipe Structuring** (10-30s)
- Calls GPT-4o API
- Combines all extracted data
- Structures as JSON
- Estimates nutrition

## 🧪 Testing

### **Debug Pipeline**
```bash
python debug_pipeline.py "https://www.youtube.com/shorts/dQw4w9WgXcQ"
```

### **Real Pipeline Test**
```bash
python test_pipeline_real.py
```

### **Test Individual Modules**
```bash
python -c "
import asyncio
from app.ai.recipe_extractor import VideoDownloader
asyncio.run(VideoDownloader.download('https://...', '/tmp/video'))
"
```

## 📈 Performance

| Stage | Time | Notes |
|-------|------|-------|
| Video Download | 30-60s | Depends on video size |
| Frame Extraction | 10-30s | Parallelizable |
| Audio Extraction | 5-10s | Optional |
| Transcription | 30-90s | Model inference |
| OCR | 20-60s | Per-frame processing |
| YOLO | 10-30s | GPU-accelerated if available |
| LLM | 10-30s | API call overhead |
| **Total** | **2-5 min** | End-to-end |

## 🚀 Deployment

### **Development**
```bash
python -m uvicorn main:app --reload
```

### **Production**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker**
```bash
docker-compose up
```

### **Heroku/Railway**
```bash
# Push to platform
git push heroku main

# Or export docker image
docker tag kalo-backend:latest myregistry/kalo-backend:latest
docker push myregistry/kalo-backend:latest
```

## 📱 iOS Integration

See [iOS_INTEGRATION_GUIDE.md](iOS_INTEGRATION_GUIDE.md) for detailed iOS app integration instructions.

## 🔐 Security

- API keys stored in `.env` (never committed)
- CORS configured for frontend domains
- Input validation on all endpoints
- SQL injection prevention with ORM
- Rate limiting recommended for production

## 📝 Logging

All components log detailed information:

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Or from console output
2025-12-07 00:16:52 - app.ai.recipe_extractor - INFO - ✓ Video download successful
```

## 🎯 Roadmap

- [ ] Fine-tune model on cooking video dataset
- [ ] Support for multiple recipe formats
- [ ] Dietary restriction preferences
- [ ] Multi-language support
- [ ] Recipe history/persistence
- [ ] Nutrition database integration
- [ ] Batch processing
- [ ] WebSocket real-time updates
- [ ] Advanced image processing
- [ ] Custom OCR training

## 🤝 Contributing

Contributions welcome! Areas needing help:

- [ ] Performance optimization
- [ ] Additional food detection models
- [ ] Extended language support
- [ ] Better macro estimation
- [ ] UI improvements

## 📞 Support

- **Documentation**: See [COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)
- **Troubleshooting**: See Troubleshooting section above
- **Issues**: Create GitHub issue
- **Email**: support@kalo.app

## 📄 License

MIT License - See LICENSE file

---

**Status**: ✅ Production Ready (v1.0.0)

**Last Updated**: December 7, 2025

**Maintained By**: KALO Engineering Team
