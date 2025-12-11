"""
Celery Configuration
For background task processing (recipe extraction, etc.)
"""
from celery import Celery
from kombu import Exchange, Queue
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
app = Celery(
    'kalo_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit
    
    # Task routing
    task_routes={
        'app.tasks.recipe.*': {'queue': 'recipe_extraction'},
        'app.tasks.meal.*': {'queue': 'meal_planning'},
        'app.tasks.workout.*': {'queue': 'workout_generation'},
    },
    
    # Define queues
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('recipe_extraction', Exchange('recipes'), routing_key='recipe.*'),
        Queue('meal_planning', Exchange('meals'), routing_key='meal.*'),
        Queue('workout_generation', Exchange('workouts'), routing_key='workout.*'),
    ),
)

@app.task(bind=True)
def debug_task(self):
    """Test task for debugging"""
    print(f'Request: {self.request!r}')
    return 'Task executed successfully'
