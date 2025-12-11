# KALO IMPLEMENTATION ROADMAP - PHASES 3-8

## 📋 Overview

This document provides **detailed implementation specs** for Phases 3-8, enabling each agent to work independently.

---

# PHASE 3: STRONG-STYLE WORKOUT FEATURES

## Status: READY FOR IMPLEMENTATION

### Backend (Already Mostly Complete)

**Models** (Already in `app/models/models.py`):
```python
class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    title = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    duration_s = Column(Integer, nullable=False)  # Duration in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    
    id = Column(String, primary_key=True)
    workout_id = Column(String, ForeignKey("workouts.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Bench Press"
    order = Column(Integer, nullable=False)  # Sequence in workout
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    
    id = Column(String, primary_key=True)
    workout_exercise_id = Column(String, ForeignKey("workout_exercises.id"))
    set_index = Column(Integer, nullable=False)  # 1, 2, 3, etc
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    rpe = Column(Integer, nullable=True)  # Rate of Perceived Exertion (1-10)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Endpoints** (Already in `app/api/workouts.py`):
- `POST /api/workouts` - Log workout
- `GET /api/workouts` - List workouts
- `GET /api/workouts/{id}` - Get workout detail
- `PUT /api/workouts/{id}` - Update workout
- `GET /api/workouts/{id}/best-lifts` - Get PR for each exercise (TODO)

### iOS Implementation

**Create `kalo/kalo/ViewModels/WorkoutViewModel.swift`**:
- Fetch workouts from API
- Track personal records (PRs) per exercise
- Calculate volume (reps × weight)

**Create `kalo/kalo/Views/Workouts/WorkoutHistoryView.swift`**:
- List all workouts (sorted by date, newest first)
- Show date, title, duration
- Tap to see detail

**Create `kalo/kalo/Views/Workouts/WorkoutDetailView.swift`**:
- Show all exercises with sets
- Display PR badges (new PR ✨ if weight > previous)
- Show sets table: Set # | Reps | Weight | RPE
- Edit button (optional)

**Create `kalo/kalo/Views/Workouts/LogWorkoutView.swift`**:
- Title input (e.g., "Chest & Triceps")
- Add exercises (name, set 1: reps/weight/RPE)
- Add more sets button
- Duration timer (or manual entry)
- Save button (POST to /api/workouts)
- Show loading state and error handling

**Design**:
- Use KaloTheme.mint for PR badges
- Card layout for each exercise
- Apple-style tabular data for sets
- Smooth animations on PR

---

# PHASE 4: RUNNING + MAPS + ROUTE SHARING

## Status: READY FOR IMPLEMENTATION

### Backend (Already Complete)

All endpoints ready in `/api/runs`:
- `POST /api/runs/start` → session
- `POST /api/runs/{session_id}/update` → live tracking
- `POST /api/runs/{session_id}/finish` → saves run with route_points
- `GET /api/runs` → history
- `GET /api/runs/{id}` → detail with route_points
- `GET /api/runs/summary/stats` → stats
- `GET /api/runs/heatmap/data` → calendar data

### iOS Implementation

**Create `kalo/kalo/ViewModels/RunTrackingViewModel.swift`**:
- Manage run session (start/update/finish)
- Track CoreLocation updates
- Calculate distance, pace, calories on-the-fly
- Timer for elapsed time

**Create `kalo/kalo/Views/Running/RunTrackingView.swift`**:
- Large distance display (e.g., "10.5 KM")
- Pace display (e.g., "6:00 /KM")
- Duration timer
- Calories burned
- Start → Pause/Resume → Finish buttons
- Map showing current position + route (MapKit)
- Real-time location permission request

**Create `kalo/kalo/Views/Running/RunDetailView.swift`**:
- Read-only view of completed run
- Distance, duration, pace, elevation gain, calories
- MapKit showing full route from route_points
- Share button

**Create `kalo/kalo/Views/Running/RunShareCardView.swift`**:
- Generates share image with:
  - Kalo logo + "Activity"
  - Distance, duration, pace
  - Small map thumbnail
  - Mint + white branding
- Uses SwiftUI Canvas or UIGraphicsPDFRenderer
- Exports to PNG
- Opens UIActivityViewController for sharing

**Models** (Create `kalo/kalo/Models/RunTracking.swift`):
```swift
struct RunSession: Codable {
    let sessionId: String
    let startedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case startedAt = "started_at"
    }
}

struct Run: Codable {
    let id: String
    let distanceM: Float
    let durationS: Int
    let avgPaceSpKm: Float
    let caloriesBurned: Int?
    let elevationGainM: Float?
    let startedAt: Date
    let endedAt: Date
    let routePoints: [GPSPoint]
    
    enum CodingKeys: String, CodingKey {
        case id, distanceM = "distance_m", durationS = "duration_s"
        case avgPaceSpKm = "avg_pace_s_per_km"
        case caloriesBurned = "calories_burned"
        case elevationGainM = "elevation_gain_m"
        case startedAt = "started_at"
        case endedAt = "ended_at"
        case routePoints = "route_points"
    }
}

struct GPSPoint: Codable {
    let lat: Double
    let lng: Double
    let timestamp: Date?
}
```

**Requirements**:
- Request NSLocationWhenInUseUsageDescription
- Add CoreLocation import
- Use CLLocationManager for real-time tracking
- Call `/api/runs/update` every 10 seconds with current location
- Show permission alert if location denied

---

# PHASE 5: ACTIVITY HEATMAP VIEW

## Backend (Already Complete)

`GET /api/runs/heatmap/data?period=week|month|year` returns:
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
    ...
  ]
}
```

## iOS Implementation

**Create `kalo/kalo/Views/Activity/ActivityHeatmapView.swift`**:
- Calendar grid view (7 columns × 6 rows per month, or week view)
- Each day cell:
  - Date number
  - Background color based on intensity (0-1):
    - 0.0 = white / light gray
    - 0.5 = mint 50%
    - 1.0 = mint 100%
  - Tap to show day detail (distance, time, run count)
- Period selector: Week / Month / Year buttons at top
- Fetches from `/api/runs/heatmap/data?period=...`

**Design**:
- Cell size: 48×48pt
- Corner radius: 8pt
- Font: system caption
- Colors:
  - No activity: #F0F0F0
  - Partial: mint at opacity (intensity)
  - Full: KaloTheme.mint
- Smooth animation on period change

---

# PHASE 6: SOCIAL FEED (STRAVA-STYLE)

## Backend (Already Complete)

Endpoints:
- `GET /api/posts/feed` → List posts (runs, workouts, meals)
- `POST /api/posts` → Create post
- `POST /api/posts/{id}/like` → Like post
- `POST /api/posts/{id}/comments` → Comment on post

## iOS Implementation

**Create `kalo/kalo/Views/Social/SocialFeedView.swift`**:
- Vertical list of post cards
- Infinite scroll (pagination)
- Pull-to-refresh

**Create `kalo/kalo/Views/Social/PostCardView.swift`**:
Shows different card types:

1. **Run Post**:
   - User avatar + name
   - Quote: "Just crushed a 10km run!"
   - Stats card: distance | duration | pace
   - Small map thumbnail (optional)
   - Like button (heart icon) + count
   - Comment icon + count

2. **Workout Post**:
   - User avatar + name
   - Quote: "Chest & triceps day"
   - Exercises list: "Bench Press 3×8 @ 80kg"
   - Like button + count

3. **Meal/Recipe Post**:
   - User avatar + name
   - Quote: "Made carbonara!"
   - Recipe image thumbnail
   - Macros: 500cal | 20g protein | 60g carbs | 15g fat
   - Like button + count

**Create `kalo/kalo/Views/Social/CreatePostView.swift`**:
- Post type selector: Run / Workout / Meal / Recipe
- If Run selected:
  - List recent runs (last 7 days)
  - Select run → shows stats in preview
- Text input for caption
- Optional image upload
- Post button (POST to /api/posts)

**Models** (Create `kalo/kalo/Models/Post.swift`):
```swift
struct Post: Codable, Identifiable {
    let id: String
    let userId: String
    let username: String
    let type: PostType  // "run", "workout", "meal", "recipe"
    let content: String
    let runId: String?
    let runStats: RunStats?  // if type == "run"
    let workoutStats: WorkoutStats?  // if type == "workout"
    let likesCount: Int
    let commentsCount: Int
    let userLiked: Bool
    let createdAt: Date
    
    enum PostType: String, Codable {
        case run, workout, meal, recipe
    }
}

struct RunStats: Codable {
    let distanceM: Float
    let durationS: Int
    let pace: String
    
    enum CodingKeys: String, CodingKey {
        case distanceM = "distance_m"
        case durationS = "duration_s"
        case pace
    }
}
```

---

# PHASE 7: DESIGN CONSISTENCY PASS

## Requirements

All new screens must:

1. **Colors**:
   - Accent: KaloTheme.mint (#4BE3C1)
   - Background: white
   - Text: #1A1A1A
   - Dividers: #ECECEC

2. **Typography**:
   - Title: .system(size: 28, weight: .bold)
   - Large: .system(size: 18, weight: .semibold)
   - Body: .system(size: 16, weight: .regular)
   - Caption: .system(size: 13, weight: .regular)

3. **Spacing**:
   - Padding: 16pt
   - Section gap: 24pt
   - Item gap: 12pt
   - Corner radius: 12-16pt

4. **Cards**:
   - Background: white
   - Corner radius: 16pt
   - Shadow: black 8% opacity, 8pt blur
   - Padding: 16pt

5. **Buttons**:
   - Primary: mint background, white text, 12pt corner radius
   - Secondary: white background, mint text, 1pt border
   - Min height: 44pt

6. **Reusable Components** (create if missing):
   - `SectionHeaderView(title: String)` - Styled section titles
   - `StatCardView(title: String, value: String, unit: String?)` - Stats display
   - `ProgressRingView(progress: Double, lineWidth: CGFloat)` - Circular progress
   - `ActivityCardView(...)` - Generic activity card

---

# PHASE 8: INTEGRATION TESTING & DOCUMENTATION

## Testing Checklist

- [ ] Backend started: `python main.py`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] iOS compiles: `Cmd+B`
- [ ] Network test passes (health check from app)
- [ ] Runs: Create → Update → Finish → List
- [ ] Challenges: List → Join → View leaderboard
- [ ] Workouts: Create → View history → View detail
- [ ] Social: View feed → Create post → Like post
- [ ] Heatmap: Load weekly → monthly → yearly
- [ ] Share: Create share card → UIActivityViewController shows

## Documentation

Create these files:
- **RUNNING_IMPLEMENTATION.md** - Complete run tracking guide
- **WORKOUT_GUIDE.md** - Workout logging & PR tracking
- **SOCIAL_GUIDE.md** - Social feed features
- **API_INTEGRATION_CHECKLIST.md** - For QA/testing

---

## 🚀 QUICK START FOR EACH AGENT

### Workouts Agent (Phase 3)
1. Implement `WorkoutViewModel.swift` (data fetching)
2. Create `LogWorkoutView.swift` (add new workout)
3. Create `WorkoutHistoryView.swift` (list)
4. Create `WorkoutDetailView.swift` (detail + PR badges)
5. Test with: `curl -X POST http://localhost:8000/api/workouts ...`

### Running Agent (Phase 4)
1. Implement `RunTrackingViewModel.swift` (CoreLocation + API)
2. Create `RunTrackingView.swift` (live tracking with map)
3. Create `RunDetailView.swift` (view completed run)
4. Create `RunShareCardView.swift` (generate & share)
5. Test with: Run start → update → finish workflow

### Heatmap Agent (Phase 5)
1. Create `ActivityHeatmapView.swift` (calendar grid)
2. Fetch `/api/runs/heatmap/data` and color cells
3. Test with: Week / Month / Year toggles

### Social Agent (Phase 6)
1. Create `SocialFeedView.swift` (list posts)
2. Create `PostCardView.swift` (render different post types)
3. Create `CreatePostView.swift` (compose new post)
4. Test with: POST to `/api/posts`, like, comment

### Design Agent (Phase 7)
1. Audit all new views for color/spacing consistency
2. Extract repeated patterns to `SharedComponents.swift`
3. Apply KaloTheme throughout
4. Test on iPhone 12-15 sizes

### Orchestrator (Phase 8)
1. Write comprehensive testing guide
2. Create Postman collection for all endpoints
3. Verify end-to-end flows
4. Deploy documentation

---

## 📊 Status Matrix

| Phase | Component | Backend | iOS | Status |
|-------|-----------|---------|-----|--------|
| 1 | Networking | ✅ | ✅ | DONE |
| 2 | API Docs | ✅ | ✅ | DONE |
| 3 | Workouts | ✅ | ⏳ | READY |
| 4 | Running | ✅ | ⏳ | READY |
| 5 | Heatmap | ✅ | ⏳ | READY |
| 6 | Social | ✅ | ⏳ | READY |
| 7 | Design | — | ⏳ | READY |
| 8 | Testing | — | ⏳ | READY |

---

## 💡 Key Implementation Tips

1. **Use existing patterns** from Activity/Recipes for consistency
2. **Reuse NetworkingService** for all API calls
3. **Apply KaloTheme everywhere** - no custom colors
4. **Add haptic feedback** using `HapticsService`
5. **Test on simulator first**, then physical device
6. **Use async/await** throughout
7. **Handle network errors gracefully** with user-friendly messages
8. **Mock data while testing** if backend not available

---

**Next: Each agent implements their phase independently using these specs!**
