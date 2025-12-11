"""
Celery Application Configuration
Configure Celery for async task processing with Redis broker
"""

import os
from celery import Celery
from kombu import Exchange, Queue
from dotenv import load_dotenv

load_dotenv()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Create Celery app
celery_app = Celery(
    "kalo",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.ai.tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Broker settings
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_extended=True,
    
    # Task routing
    task_routes={
        "app.ai.tasks.extract_recipe_async": {"queue": "ai"},
        "app.ai.tasks.generate_meal_plan_async": {"queue": "ai"},
        "app.ai.tasks.generate_workout_plan_async": {"queue": "ai"},
    },
    
    # Queues
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("ai", Exchange("ai"), routing_key="ai.#"),
        Queue("priority", Exchange("priority"), routing_key="priority.#"),
    ),
    
    # Scheduling (if using Celery Beat)
    beat_scheduler="celery.beat:PersistentScheduler",
)


# Task autodiscovery
celery_app.autodiscover_tasks(["app"])

print(f"✅ Celery configured with broker: {CELERY_BROKER_URL}")
