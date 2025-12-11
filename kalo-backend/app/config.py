"""
Configuration and environment variables
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database - SQLite for dev (no setup), PostgreSQL for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./kalo.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # S3
    AWS_S3_BUCKET: str = "kalo-media"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    
    # AI Models
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    OCR_MODEL: str = "paddleocr"
    FOOD_DETECTION_MODEL: str = "yolov8n"
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # "openai", "llama" (Ollama), or "auto"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_TEXT: str = "gpt-4o-mini"  # Cheap text model
    OPENAI_MODEL_VISION: str = "gpt-4o"  # Vision-capable model
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Pydantic v2 configuration - CORRECT SYNTAX
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars not defined in Settings
        case_sensitive=False
    )

settings = Settings()
