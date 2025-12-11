# KALO Backend API - Complete Reference

## 🎯 Status: Phase 2 COMPLETE

All core endpoints are implemented and documented below.

---

## 📋 TABLE OF CONTENTS

1. [Health & System](#health--system)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Running & Activity](#running--activity)
5. [Challenges](#challenges)
6. [Workouts](#workouts)
7. [Recipes & AI](#recipes--ai)
8. [Meal Planning](#meal-planning)
9. [Social & Posts](#social--posts)
10. [Example cURL Commands](#example-curl-commands)

---

## Health & System

### GET /health
Quick health check for iOS connectivity testing.

```bash
curl http://localhost:8000/health
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "kalo-api",
  "version": "1.0.0",
  "timestamp": "2025-12-07T12:34:56.789Z",
  "platform": "Darwin",
  "message": "API is running and accepting connections from iOS"
}
```

---

### GET /health/verbose
Detailed health check including database connectivity.

```bash
curl http://localhost:8000/health/verbose
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "timestamp": "2025-12-07T12:34:56.789Z"
  },
  "platform": "Darwin",
  "endpoints_available": [
    "/api/auth", "/api/users", "/api/recipes", "/api/mealplan",
    "/api/grocery", "/api/workouts", "/api/runs", "/api/posts",
    "/api/challenges", "/api/ai"
  ]
}
```

---

## Authentication

### POST /api/auth/register
Register a new user.

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "name": "John Doe"
  }'
```

**Response (201 Created)**:
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "User registered successfully"
}
```

---

### POST /api/auth/login
Authenticate user and get JWT token.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Running & Activity

### POST /api/runs/start
Start a new run session.

```bash
curl -X POST http://localhost:8000/api/runs/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK)**:
```json
{
  "session_id": "run-session-uuid",
  "started_at": "2025-12-07T12:00:00Z",
  "message": "Run session started. Use this session_id to update and finish."
}
```

---

### POST /api/runs/{session_id}/update
Update active run with live data (distance, GPS, etc).

```bash
curl -X POST http://localhost:8000/api/runs/run-session-uuid/update \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_distance_m": 2500.5,
    "route_points": [
      {
        "lat": 37.7749,
        "lng": -122.4194,
        "timestamp": "2025-12-07T12:00:10Z"
      },
      {
        "lat": 37.7750,
        "lng": -122.4195,
        "timestamp": "2025-12-07T12:00:15Z"
      }
    ]
  }'
```

**Response (200 OK)**:
```json
{
  "session_id": "run-session-uuid",
  "current_distance_m": 2500.5,
  "elapsed_seconds": 900,
  "current_pace_s_per_km": 360.0,
  "message": "Run session updated"
}
```

---

### POST /api/runs/{session_id}/finish
Complete run session and save to history.

```bash
curl -X POST http://localhost:8000/api/runs/run-session-uuid/finish \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "final_distance_m": 10000.0,
    "final_duration_s": 3600,
    "elevation_gain_m": 150,
    "calories_burned": 600
  }'
```

**Response (200 OK)**:
```json
{
  "id": "run-uuid",
  "distance_m": 10000.0,
  "duration_s": 3600,
  "avg_pace_s_per_km": 360.0,
  "calories_burned": 600,
  "elevation_gain_m": 150,
  "started_at": "2025-12-07T12:00:00Z",
  "ended_at": "2025-12-07T13:00:00Z",
  "route_points": [...],
  "created_at": "2025-12-07T13:00:05Z",
  "updated_at": "2025-12-07T13:00:05Z"
}
```

---

### GET /api/runs
List user's run history.

```bash
# Get last 10 runs
curl "http://localhost:8000/api/runs?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by date range
curl "http://localhost:8000/api/runs?start_date=2025-12-01&end_date=2025-12-07" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
[
  {
    "id": "run-uuid-1",
    "distance_m": 10000.0,
    "duration_s": 3600,
    "avg_pace_s_per_km": 360.0,
    "calories_burned": 600,
    "elevation_gain_m": 150,
    "started_at": "2025-12-07T12:00:00Z",
    "ended_at": "2025-12-07T13:00:00Z",
    "route_points": [...]
  },
  ...
]
```

---

### GET /api/runs/{run_id}
Get detailed info for a specific run.

```bash
curl http://localhost:8000/api/runs/run-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: Same as finish response above.

---

### GET /api/runs/summary/stats?period=week
Get run summary stats (total distance, time, count, calories).

```bash
# Weekly stats
curl "http://localhost:8000/api/runs/summary/stats?period=week" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Monthly
curl "http://localhost:8000/api/runs/summary/stats?period=month" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Yearly
curl "http://localhost:8000/api/runs/summary/stats?period=year" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "total_distance_m": 45000.0,
  "total_time_s": 16200,
  "number_of_runs": 4,
  "average_pace_s_per_km": 360.0,
  "total_calories": 2400,
  "per_day_breakdown": [
    {
      "date": "2025-12-07",
      "distance_m": 10000.0,
      "time_s": 3600,
      "runs_count": 1,
      "intensity": 0.5
    },
    {
      "date": "2025-12-06",
      "distance_m": 8000.0,
      "time_s": 2880,
      "runs_count": 1,
      "intensity": 0.4
    }
  ]
}
```

---

### GET /api/runs/heatmap/data?period=week
Get calendar heatmap data (date → activity volume).

```bash
curl "http://localhost:8000/api/runs/heatmap/data?period=week" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "period": "week",
  "data": [
    {
      "date": "2025-12-07",
      "distance_m": 10000.0,
      "time_s": 3600,
      "runs_count": 1,
      "intensity": 1.0
    },
    {
      "date": "2025-12-06",
      "distance_m": 8000.0,
      "time_s": 2880,
      "runs_count": 1,
      "intensity": 0.8
    },
    {
      "date": "2025-12-05",
      "distance_m": 0.0,
      "time_s": 0,
      "runs_count": 0,
      "intensity": 0.0
    }
  ]
}
```

---

## Challenges

### GET /api/challenges
List all available challenges.

```bash
curl http://localhost:8000/api/challenges \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
[
  {
    "id": "challenge-uuid",
    "title": "December 10K Challenge",
    "description": "Run 10km this December",
    "challenge_type": "distance_goal",
    "target_value": 10000.0,
    "start_date": "2025-12-01",
    "end_date": "2025-12-31",
    "reward_points": 500
  },
  ...
]
```

---

### GET /api/challenges/{challenge_id}
Get challenge details with user progress and leaderboard.

```bash
curl http://localhost:8000/api/challenges/challenge-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
{
  "id": "challenge-uuid",
  "title": "December 10K Challenge",
  "description": "Run 10km this December",
  "challenge_type": "distance_goal",
  "target_value": 10000.0,
  "start_date": "2025-12-01",
  "end_date": "2025-12-31",
  "reward_points": 500,
  "user_progress": 5000.0,
  "user_percentage": 50.0,
  "user_status": "in_progress",
  "days_remaining": 24,
  "leaderboard": [
    {
      "user_id": "user-1",
      "username": "alice",
      "current_progress": 10000.0,
      "percentage": 100.0,
      "position": 1,
      "status": "completed"
    },
    {
      "user_id": "your-user-id",
      "username": "your_name",
      "current_progress": 5000.0,
      "percentage": 50.0,
      "position": 2,
      "status": "in_progress"
    }
  ]
}
```

---

### POST /api/challenges/{challenge_id}/join
Join a challenge.

```bash
curl -X POST http://localhost:8000/api/challenges/challenge-uuid/join \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK)**:
```json
{
  "participation_id": "participation-uuid",
  "challenge_id": "challenge-uuid",
  "user_id": "your-user-id",
  "joined_at": "2025-12-07T12:34:56Z",
  "message": "Successfully joined challenge"
}
```

---

### POST /api/challenges/{challenge_id}/leave
Leave a challenge.

```bash
curl -X POST http://localhost:8000/api/challenges/challenge-uuid/leave \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK)**:
```json
{
  "message": "Successfully left challenge"
}
```

---

### GET /api/challenges/{challenge_id}/leaderboard
Get challenge leaderboard.

```bash
curl http://localhost:8000/api/challenges/challenge-uuid/leaderboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: Array of leaderboard entries (same as in challenge detail above).

---

## Workouts

### GET /api/workouts
List user's workouts.

```bash
curl "http://localhost:8000/api/workouts?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
[
  {
    "id": "workout-uuid",
    "date": "2025-12-07",
    "title": "Chest & Triceps",
    "notes": "Strong session",
    "duration_s": 2400,
    "exercises": [
      {
        "name": "Bench Press",
        "sets": [
          { "reps": 8, "weight_kg": 80.0, "rpe": 8 },
          { "reps": 8, "weight_kg": 80.0, "rpe": 8 },
          { "reps": 6, "weight_kg": 85.0, "rpe": 9 }
        ]
      }
    ]
  }
]
```

---

### POST /api/workouts
Log a new workout.

```bash
curl -X POST http://localhost:8000/api/workouts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chest & Triceps",
    "notes": "Strong session",
    "duration_s": 2400,
    "exercises": [
      {
        "name": "Bench Press",
        "order": 1,
        "sets": [
          { "set_index": 1, "reps": 8, "weight_kg": 80.0, "rpe": 8 },
          { "set_index": 2, "reps": 8, "weight_kg": 80.0, "rpe": 8 },
          { "set_index": 3, "reps": 6, "weight_kg": 85.0, "rpe": 9 }
        ]
      }
    ]
  }'
```

**Response (201 Created)**: Same as GET response above.

---

## Recipes & AI

### POST /api/ai/extract-recipe
Start recipe extraction from video URL.

```bash
curl -X POST http://localhost:8000/api/ai/extract-recipe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

**Response (202 Accepted)**:
```json
{
  "task_id": "celery-task-uuid",
  "status": "pending",
  "message": "Recipe extraction started",
  "progress": "[1/5] Downloading video..."
}
```

---

### GET /api/ai/extract-recipe/{task_id}/status
Poll extraction status.

```bash
curl http://localhost:8000/api/ai/extract-recipe/celery-task-uuid/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (while processing)**:
```json
{
  "task_id": "celery-task-uuid",
  "status": "processing",
  "progress": "[3/5] Extracting ingredients...",
  "recipe": null
}
```

**Response (completed)**:
```json
{
  "task_id": "celery-task-uuid",
  "status": "completed",
  "progress": "[5/5] Complete",
  "recipe": {
    "title": "Spaghetti Carbonara",
    "ingredients": [
      { "name": "spaghetti", "amount": 400, "unit": "g" },
      { "name": "eggs", "amount": 4, "unit": "piece" }
    ],
    "steps": [
      "Boil water and cook pasta",
      "Beat eggs with cheese"
    ],
    "cook_time_minutes": 20,
    "servings": 4,
    "macros": {
      "calories": 500,
      "protein": 20,
      "carbs": 60,
      "fat": 15
    }
  }
}
```

---

## Meal Planning

### POST /api/ai/mealplan/generate
Generate AI meal plan.

```bash
curl -X POST http://localhost:8000/api/ai/mealplan/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "daily_calories": 2000,
    "macro_targets": {
      "protein_percent": 30,
      "carbs_percent": 50,
      "fat_percent": 20
    },
    "diet_type": "balanced",
    "restrictions": ["dairy-free"]
  }'
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "meal_plan": {
    "week_1": {
      "monday": {
        "breakfast": {...},
        "lunch": {...},
        "dinner": {...},
        "snack": {...}
      }
    }
  }
}
```

---

## Social & Posts

### GET /api/posts/feed
Get social feed (recent posts from users).

```bash
curl "http://localhost:8000/api/posts/feed?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK)**:
```json
[
  {
    "id": "post-uuid",
    "user_id": "user-uuid",
    "username": "alice",
    "type": "run",
    "content": "Just crushed a 10km run!",
    "run_id": "run-uuid",
    "run_stats": {
      "distance_m": 10000,
      "duration_s": 3600,
      "pace": "6:00/km"
    },
    "likes_count": 5,
    "comments_count": 2,
    "user_liked": false,
    "created_at": "2025-12-07T12:00:00Z"
  }
]
```

---

### POST /api/posts
Create a new post.

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "run",
    "content": "Just crushed a 10km run!",
    "run_id": "run-uuid"
  }'
```

**Response (201 Created)**:
```json
{
  "id": "post-uuid",
  "user_id": "your-user-id",
  "username": "your_username",
  "type": "run",
  "content": "Just crushed a 10km run!",
  "run_id": "run-uuid",
  "likes_count": 0,
  "comments_count": 0,
  "user_liked": false,
  "created_at": "2025-12-07T12:34:56Z"
}
```

---

### POST /api/posts/{post_id}/like
Like a post.

```bash
curl -X POST http://localhost:8000/api/posts/post-uuid/like \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK)**:
```json
{
  "message": "Post liked",
  "likes_count": 6
}
```

---

## Example cURL Commands

### Test Basic Connectivity
```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Verbose health check
curl http://localhost:8000/health/verbose
```

### Register & Login
```bash
# Register
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123",
    "name": "Test User"
  }')

echo $TOKEN_RESPONSE | jq .

# Extract token from response and use for other calls
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.token')

# Or login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
```

### Run Tracking Workflow
```bash
# 1. Start a run
START=$(curl -s -X POST http://localhost:8000/api/runs/start \
  -H "Authorization: Bearer $TOKEN")

SESSION_ID=$(echo $START | jq -r '.session_id')
echo "Run session: $SESSION_ID"

# 2. Update every 10 seconds during run
curl -s -X POST http://localhost:8000/api/runs/$SESSION_ID/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_distance_m": 1000,
    "route_points": []
  }' | jq .

# 3. Finish the run
curl -s -X POST http://localhost:8000/api/runs/$SESSION_ID/finish \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "final_distance_m": 10000,
    "final_duration_s": 3600,
    "calories_burned": 600
  }' | jq .

# 4. Get runs
curl http://localhost:8000/api/runs \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. Get summary stats
curl "http://localhost:8000/api/runs/summary/stats?period=week" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Get heatmap
curl "http://localhost:8000/api/runs/heatmap/data?period=week" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## 🎯 API Status Summary

| Feature | GET | POST | PUT | DELETE | Status |
|---------|-----|------|-----|--------|--------|
| Health | ✅ | — | — | — | ✅ Ready |
| Auth | — | ✅ | — | — | ✅ Ready |
| Runs | ✅ | ✅ | — | — | ✅ Ready |
| Challenges | ✅ | ✅ | — | — | ✅ Ready |
| Workouts | ✅ | ✅ | — | — | ✅ Ready |
| Recipes | ✅ | ✅ | — | — | ✅ Ready |
| Social Posts | ✅ | ✅ | — | — | ✅ Ready |

**All endpoints documented and ready for iOS integration!**
