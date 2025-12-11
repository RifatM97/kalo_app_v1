# Kalo Backend Setup Guide

Complete setup instructions for the Kalo backend with AI recipe extraction pipeline.

## Prerequisites

- Python 3.9+
- FFmpeg installed on system
- Redis server (for Celery background tasks)
- OpenAI API key or Anthropic API key

## System Dependencies

### macOS (Using Homebrew)

```bash
# Install FFmpeg
brew install ffmpeg

# Install Redis
brew install redis

# Verify installations
ffmpeg -version
redis-cli --version
```

### Ubuntu/Debian

```bash
# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Install Redis
sudo apt-get install redis-server

# Verify installations
ffmpeg -version
redis-cli --version
```

### Windows (Using Chocolatey)

```bash
# Install FFmpeg
choco install ffmpeg

# Install Redis (or use Windows Subsystem for Linux)
choco install redis

# Verify installations
ffmpeg -version
redis-cli --version
```

## Python Environment Setup

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd kalo-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 3. Download AI Models (First Run Only)

```bash
# Download Whisper-small model (~461MB)
# This happens automatically on first transcription
# But you can pre-download:
python -c "import whisper; whisper.load_model('small')"

# Download YOLOv8 model (~6MB)
# This happens automatically on first detection
# But you can pre-download:
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## Configuration

### 1. Environment Variables

Create `.env` file in `kalo-backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kalo_db
SQLALCHEMY_ECHO=True

# API Keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxx  # For LLM recipe structuring
# OR use Anthropic instead:
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# LLM Configuration
LLM_PROVIDER=openai  # or 'anthropic'
LLM_MODEL=gpt-3.5-turbo  # or 'claude-3-sonnet-20240229'

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Pipeline
WHISPER_MODEL_SIZE=small  # tiny, base, small, medium, large
OCR_CONFIDENCE_THRESHOLD=0.5
VISION_CONFIDENCE_THRESHOLD=0.5
MAX_VIDEO_LENGTH_SECONDS=600  # 10 minutes
VIDEO_DOWNLOAD_TIMEOUT=30
TRANSCRIPTION_TIMEOUT=300
EXTRACTION_TIMEOUT=1800  # 30 minutes

# File Storage
TEMP_FILES_DIR=./temp_media
S3_BUCKET_NAME=kalo-media  # Optional: if using S3
S3_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/kalo.log

# Environment
ENVIRONMENT=development  # development, staging, production
DEBUG=True
```

### 2. Database Setup

```bash
# Initialize database with Alembic
alembic upgrade head

# Or create tables directly (if not using migrations)
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 3. Redis Setup

Start Redis server:

```bash
# macOS/Linux:
redis-server

# or run in background:
redis-server --daemonize yes

# Windows (if installed via Chocolatey):
redis-server.exe
```

Verify Redis connection:

```bash
redis-cli ping
# Should return: PONG
```

## Running the Application

### 1. Start Celery Worker (For Background Tasks)

In a separate terminal:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A app.ai.tasks worker --loglevel=info

# Optional: Start with multiple workers
celery -A app.ai.tasks worker --concurrency=4 --loglevel=info
```

### 2. Start FastAPI Server

In another terminal:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run with Gunicorn for production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. (Optional) Start Celery Flower Dashboard

For monitoring background tasks:

```bash
# Install flower
pip install flower

# Start flower
celery -A app.ai.tasks flower --port=5555
```

Access dashboard: http://localhost:5555

## Quick Test

### Test Video Recipe Extraction

```python
# test_extraction.py
import asyncio
from app.ai.ai_pipeline import RecipeExtractionPipeline

async def test_extraction():
    # Initialize pipeline
    pipeline = RecipeExtractionPipeline(
        llm_provider="openai",
        whisper_model_size="small"
    )
    
    # Run extraction on sample video
    video_url = "https://www.tiktok.com/video/XXXXXXXXX"  # Replace with real URL
    
    try:
        recipe = await pipeline.run(video_url, num_frames=5)
        print("✅ Extraction successful!")
        print(f"Recipe: {recipe['title']}")
        print(f"Ingredients: {len(recipe['ingredients'])} items")
        print(f"Steps: {len(recipe['steps'])} steps")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")

# Run test
if __name__ == "__main__":
    asyncio.run(test_extraction())
```

Run test:

```bash
python test_extraction.py
```

### Test Individual Components

```python
# test_components.py
import asyncio
from app.ai.video_downloader import VideoDownloader
from app.ai.audio_extractor import AudioExtractor
from app.ai.frame_extractor import FrameExtractor
from app.ai.whisper_transcriber import WhisperTranscriber
from app.ai.ocr_extractor import OCRExtractor
from app.ai.vision_detector import VisionDetector

async def test_components():
    video_url = "https://www.tiktok.com/video/XXXXXXXXX"
    
    # 1. Test video download
    print("[1/7] Testing video download...")
    downloader = VideoDownloader()
    video_path = await downloader.download(video_url)
    print(f"✅ Video downloaded to: {video_path}")
    
    # 2. Test audio extraction
    print("[2/7] Testing audio extraction...")
    extractor = AudioExtractor()
    audio_path = await extractor.extract_audio(video_path)
    print(f"✅ Audio extracted to: {audio_path}")
    
    # 3. Test frame extraction
    print("[3/7] Testing frame extraction...")
    frame_extractor = FrameExtractor()
    frames = await frame_extractor.extract_frames(video_path, num_frames=5)
    print(f"✅ Extracted {len(frames)} frames")
    
    # 4. Test transcription
    print("[4/7] Testing transcription...")
    transcriber = WhisperTranscriber(model_size="small")
    text = await transcriber.transcribe_to_text(audio_path)
    print(f"✅ Transcription: {text[:100]}...")
    
    # 5. Test OCR
    print("[5/7] Testing OCR...")
    ocr = OCRExtractor()
    ocr_text = await ocr.extract_all_text_from_frames(frames)
    print(f"✅ OCR text: {ocr_text[:100]}...")
    
    # 6. Test vision detection
    print("[6/7] Testing vision detection...")
    vision = VisionDetector()
    ingredients = await vision.extract_ingredients_from_frames(frames)
    print(f"✅ Detected ingredients: {ingredients}")
    
    print("\n✅ All components working!")

# Run test
if __name__ == "__main__":
    asyncio.run(test_components())
```

## Deployment

### Docker Setup

See `Dockerfile` and `docker-compose.yml` for containerized deployment.

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set database to production PostgreSQL
- [ ] Set Redis to production instance
- [ ] Configure S3 bucket for media storage
- [ ] Set API rate limits
- [ ] Enable HTTPS/SSL
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Test backup and recovery procedures
- [ ] Configure auto-scaling for Celery workers

## Troubleshooting

### Issue: FFmpeg not found

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Verify
which ffmpeg
ffmpeg -version
```

### Issue: Whisper model download fails

```bash
# Pre-download model manually
python -c "import whisper; whisper.load_model('small')"

# Or specify cache directory
export FVCORE_CACHE=./models
python -c "import whisper; whisper.load_model('small')"
```

### Issue: Redis connection refused

```bash
# Start Redis server
redis-server

# Or verify it's running
redis-cli ping

# Check if port is in use
lsof -i :6379
```

### Issue: Database connection error

```bash
# Verify PostgreSQL is running
psql --version

# Test connection
psql -h localhost -U user -d kalo_db

# Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/kalo_db
```

### Issue: Celery tasks not processing

```bash
# Verify Redis is running
redis-cli ping

# Check Celery worker logs
celery -A app.ai.tasks worker --loglevel=debug

# Verify task queue
redis-cli LLEN celery

# Monitor with Flower
celery -A app.ai.tasks flower
```

### Issue: Out of memory with large videos

```bash
# Reduce frame extraction count
num_frames=3  # Instead of 5

# Reduce Whisper model size
WHISPER_MODEL_SIZE=tiny  # Instead of small

# Increase timeout
EXTRACTION_TIMEOUT=3600  # 1 hour instead of 30 min

# Run multiple workers on different machines
# See Docker Compose for distributed setup
```

## Next Steps

1. **Test Basic Extraction**: Run `test_extraction.py` with a sample video
2. **Monitor Tasks**: Use Flower dashboard at http://localhost:5555
3. **Set Up Endpoints**: Integrate AI pipeline with FastAPI routes
4. **Add Rate Limiting**: Prevent abuse of extraction endpoints
5. **Monitor Performance**: Track extraction times and error rates
6. **Scale Workers**: Add more Celery workers as usage increases

## Support

For issues or questions:
1. Check logs: `logs/kalo.log`
2. Check Celery worker output
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Test individual components with test scripts above

## References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Celery Docs](https://docs.celeryproject.org/)
- [Whisper Docs](https://github.com/openai/whisper)
- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR)
