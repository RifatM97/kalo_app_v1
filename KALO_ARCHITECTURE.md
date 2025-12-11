# KALO — Next-Gen Super Health App
## Complete Technical Architecture

---

## PART 1: SYSTEM ARCHITECTURE

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     iOS APP (SwiftUI)                        │
│  ┌──────────────┬──────────────┬──────────────────────────┐  │
│  │   Home Tab   │ Recipes Tab  │ Planner | Grocery | Feed │  │
│  │  Dashboard   │  + Video AI  │ Social | Workouts        │  │
│  └──────────────┴──────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ (HTTPS/JWT)
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI Backend (Microservices)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Gateway                                         │  │
│  │  ├─ /auth          (JWT + Refresh)                  │  │
│  │  ├─ /users         (Profile, preferences)           │  │
│  │  ├─ /recipes       (CRUD + search)                  │  │
│  │  ├─ /recipes/ai    (Video → Recipe extraction)      │  │
│  │  ├─ /mealplan      (AI generation)                  │  │
│  │  ├─ /grocery       (Auto-generate from plan)        │  │
│  │  ├─ /workouts      (Logging, history)               │  │
│  │  ├─ /runs          (GPS tracking)                   │  │
│  │  ├─ /posts         (Social feed CRUD)               │  │
│  │  ├─ /challenges    (Gaming + proof verification)    │  │
│  │  └─ /ai            (Insights + predictions)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓ (SQL/Cache)                    ↓ (Queue)
    ┌────────────────┐          ┌────────────────────┐
    │  PostgreSQL DB │          │  Redis + Celery    │
    │  + Indexing    │          │  (Background Jobs) │
    └────────────────┘          └────────────────────┘
         ↓ (ORM)                     ↓ (Process)
    ┌────────────────┐          ┌────────────────────┐
    │  SQLAlchemy    │          │  AI Pipeline:      │
    │  Models        │          │  • Video Download  │
    │                │          │  • Transcription   │
    │                │          │  • OCR             │
    │                │          │  • Recipe Extract  │
    │                │          │  • Meal Gen        │
    └────────────────┘          │  • Workout Gen     │
                                │  • Proof Verify    │
                                └────────────────────┘
                                        ↓
                                ┌────────────────┐
                                │  S3 Bucket     │
                                │  (Media Store) │
                                └────────────────┘
```

---

## PART 2: SERVICE BREAKDOWN (Monolith with modular layers)

### Core Services Architecture

```
kalo-backend/
├── app/
│   ├── api/
│   │   ├── auth.py          → Login, signup, refresh token
│   │   ├── users.py         → Profile, settings, preferences
│   │   ├── recipes.py       → Recipe CRUD + search
│   │   ├── recipes_ai.py    → Video extraction, OCR, LLM
│   │   ├── mealplan.py      → AI meal planning
│   │   ├── grocery.py       → Auto-generate from meals
│   │   ├── workouts.py      → Workout logging
│   │   ├── runs.py          → GPS tracking + analytics
│   │   ├── posts.py         → Social feed
│   │   ├── challenges.py    → Gamification + proof
│   │   └── ai.py            → Insights engine
│   │
│   ├── models/              → SQLAlchemy ORM models
│   ├── services/            → Business logic
│   ├── ai/                  → AI/ML pipelines
│   ├── db/                  → Database setup
│   ├── schemas/             → Pydantic request/response
│   └── utils/               → Helpers, auth, media
│
├── main.py                  → FastAPI app init
├── config.py                → ENV config
├── requirements.txt         → Dependencies
└── docker-compose.yml       → Local dev stack
```

---

## PART 3: DATABASE SCHEMA (PostgreSQL)

### Tables Overview

```sql
-- Authentication & Users
users
├─ id (PK)
├─ email (UNIQUE)
├─ password_hash
├─ username
├─ avatar_url
├─ bio
├─ fitness_goals (JSON)
├─ dietary_restrictions (ARRAY)
├─ created_at

user_preferences
├─ user_id (FK)
├─ daily_calorie_goal
├─ macro_targets (JSON: {protein, carbs, fat})
├─ units (metric/imperial)

-- Recipes
recipes
├─ id (PK)
├─ user_id (FK)
├─ title
├─ description
├─ ingredients (JSONB)
├─ instructions (TEXT)
├─ calories
├─ macros (JSON)
├─ prep_time
├─ cook_time
├─ servings
├─ image_url
├─ source (user/extracted)
├─ extraction_id (FK, NULL if manual)

recipe_extractions
├─ id (PK)
├─ user_id (FK)
├─ video_url
├─ transcript (TEXT)
├─ ocr_text (TEXT)
├─ detected_ingredients (JSONB)
├─ extracted_recipe (JSONB)
├─ status (processing/completed/failed)

-- Nutrition Tracking
daily_logs
├─ id (PK)
├─ user_id (FK)
├─ date
├─ total_calories
├─ total_macros (JSON)
├─ meals (ARRAY of FK -> meals)

meals
├─ id (PK)
├─ daily_log_id (FK)
├─ recipe_id (FK)
├─ meal_type (breakfast/lunch/dinner/snack)
├─ servings
├─ logged_at

-- Meal Planning
meal_plans
├─ id (PK)
├─ user_id (FK)
├─ start_date
├─ end_date (start_date + 6 days)
├─ status (active/archived)
├─ created_at

meal_plan_days
├─ id (PK)
├─ meal_plan_id (FK)
├─ day_of_week
├─ breakfast_recipe_id (FK, NULL)
├─ lunch_recipe_id (FK, NULL)
├─ dinner_recipe_id (FK, NULL)
├─ snack_recipe_id (FK, NULL)

-- Grocery Lists
grocery_lists
├─ id (PK)
├─ user_id (FK)
├─ meal_plan_id (FK, NULL)
├─ created_from (manual/auto_from_plan)
├─ created_at

grocery_items
├─ id (PK)
├─ grocery_list_id (FK)
├─ name
├─ quantity
├─ unit
├─ checked (BOOL)
├─ estimated_price

-- Workouts
workouts
├─ id (PK)
├─ user_id (FK)
├─ type (strength/cardio/flexibility)
├─ name
├─ duration (minutes)
├─ calories_burned
├─ exercises (JSONB: [{name, sets, reps, weight}, ...])
├─ completed_at
├─ created_at

workout_plans
├─ id (PK)
├─ user_id (FK)
├─ goal (strength/weight_loss/endurance)
├─ level (beginner/intermediate/advanced)
├─ frequency (per week)
├─ equipment (ARRAY)
├─ duration_weeks
├─ created_at

-- Running/GPS
runs
├─ id (PK)
├─ user_id (FK)
├─ distance (km)
├─ duration (seconds)
├─ pace (min/km)
├─ calories_burned
├─ gps_coordinates (GEOMETRY/LINE)
├─ elevation_gain
├─ completed_at
├─ created_at

-- Social Features
posts
├─ id (PK)
├─ user_id (FK)
├─ content (TEXT)
├─ post_type (text/image/video/progress)
├─ media_urls (ARRAY)
├─ likes_count
├─ comments_count
├─ created_at

post_likes
├─ id (PK)
├─ post_id (FK)
├─ user_id (FK)
├─ created_at

comments
├─ id (PK)
├─ post_id (FK)
├─ user_id (FK)
├─ content
├─ created_at

stories
├─ id (PK)
├─ user_id (FK)
├─ media_url
├─ caption
├─ expires_at (24hrs)
├─ created_at

-- Challenges & Gamification
challenges
├─ id (PK)
├─ title
├─ description
├─ challenge_type (steps/calories/workout/nutrition)
├─ start_date
├─ end_date
├─ target_value
├─ reward_points
├─ created_at

challenge_participations
├─ id (PK)
├─ challenge_id (FK)
├─ user_id (FK)
├─ current_progress
├─ status (active/completed/failed)
├─ joined_at

challenge_proofs
├─ id (PK)
├─ participation_id (FK)
├─ proof_type (photo/gps/data)
├─ proof_url
├─ verified (BOOL)
├─ verification_reason (TEXT)
├─ verified_by_user_id (FK, NULL)
├─ verified_at

-- Creator Platform
creator_content
├─ id (PK)
├─ user_id (FK)
├─ title
├─ description
├─ video_url
├─ thumbnail_url
├─ views
├─ likes
├─ published_at
├─ created_at

-- Analytics
user_analytics
├─ id (PK)
├─ user_id (FK)
├─ date
├─ data (JSONB: {avg_calories, macros, workouts, steps, etc})

ai_insights
├─ id (PK)
├─ user_id (FK)
├─ insight_type (pattern/recommendation)
├─ content (TEXT)
├─ generated_at
```

---

## PART 4: API ROUTES & ENDPOINTS

### Authentication
```
POST   /auth/register         → Create account
POST   /auth/login            → Get JWT + refresh token
POST   /auth/refresh          → New JWT from refresh token
POST   /auth/logout           → Invalidate token
```

### Users
```
GET    /users/me              → Current user profile
PUT    /users/me              → Update profile
GET    /users/{user_id}       → View another user
GET    /users/me/preferences  → User preferences
PUT    /users/me/preferences  → Update preferences
```

### Recipes
```
GET    /recipes               → List with pagination + filters
POST   /recipes               → Create recipe
GET    /recipes/{id}          → Recipe detail
PUT    /recipes/{id}          → Update recipe
DELETE /recipes/{id}          → Delete recipe
GET    /recipes/search        → Full-text search
```

### AI Recipe Extraction
```
POST   /recipes/ai/extract    → Submit video URL
GET    /recipes/ai/extract/{id} → Check extraction status
GET    /recipes/ai/extractions → User's extraction history
```

### Meal Planning
```
GET    /mealplan              → Current week plan
POST   /mealplan              → Generate new plan (AI)
PUT    /mealplan/{id}         → Update specific meal
GET    /mealplan/history      → Past plans
```

### Grocery
```
GET    /grocery               → Current list
POST   /grocery               → Create manual list
POST   /grocery/auto          → Generate from meal plan
PUT    /grocery/{item_id}     → Check off item
DELETE /grocery/{item_id}     → Remove item
```

### Workouts
```
POST   /workouts              → Log completed workout
GET    /workouts              → History
GET    /workouts/stats        → Aggregate stats
POST   /workouts/generate     → AI workout generator
GET    /workouts/plans        → User's saved plans
```

### Running/GPS
```
POST   /runs                  → Create run (with GPS)
GET    /runs                  → Run history
GET    /runs/{id}             → Run detail + map
GET    /runs/stats            → Personal running stats
```

### Social Feed
```
GET    /posts                 → Feed (with algorithm)
POST   /posts                 → Create post
DELETE /posts/{id}            → Delete post
POST   /posts/{id}/like       → Like post
DELETE /posts/{id}/like       → Unlike post
GET    /posts/{id}/comments   → Comments
POST   /posts/{id}/comments   → Add comment
```

### Stories
```
POST   /stories               → Upload story
GET    /stories               → Current stories (24h)
DELETE /stories/{id}          → Delete story
```

### Challenges
```
GET    /challenges            → Active challenges
POST   /challenges/{id}/join  → Join challenge
GET    /challenges/{id}       → Challenge detail + leaderboard
POST   /challenges/{id}/proof → Submit proof
GET    /challenges/my         → User's challenges
```

### AI Insights
```
GET    /ai/insights           → Generated insights
GET    /ai/trends             → Pattern detection
GET    /ai/recommendations    → Personalized recommendations
```

---

## PART 5: Authentication Model

```python
# JWT Token Structure
{
  "sub": "user_id",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234571490,  # 1 hour
  "type": "access"
}

# Refresh Token
{
  "sub": "user_id",
  "type": "refresh",
  "exp": 1234654890  # 7 days
}

# Header
Authorization: Bearer <access_token>
```

---

## PART 6: Data Models (Pydantic Schemas)

See backend code in next sections.

---

## PART 7: Scalability for AI

- **Modular AI service**: `app/ai/` can be extended with new models
- **Queue-based processing**: Celery + Redis for background AI tasks
- **Plugin architecture**: New AI endpoints can be added without refactoring core
- **Config-driven**: Model parameters in environment variables
- **Versioning**: `/ai/v1/`, `/ai/v2/` for model iteration

---

## Next: See backend code implementation
