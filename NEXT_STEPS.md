# KALO Implementation Roadmap - Next Steps

**Current Status**: ✅ **Design & Core Implementation Complete**
- Backend: All 10 API modules coded + all 4 AI modules designed
- iOS: 8+ screens implemented + new models created
- Database: 18 SQLAlchemy models fully designed
- Documentation: Complete architecture + deployment guides

---

## 🚀 Phase 1: Production Readiness (1-2 weeks)

### Priority 1.1: Database Migrations
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Backend cannot persist data without migrations
**Time**: 2-3 hours
**Difficulty**: Easy

**Files to Create**:
- `kalo-backend/alembic/versions/001_initial.py` - Create all 18 tables

**Steps**:
1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init alembic` (in kalo-backend/)
3. Generate migration: `alembic revision --autogenerate -m "Initial schema"`
4. Manually verify the migration file
5. Create migration that:
   - Creates 18 tables
   - Adds all relationships (foreign keys)
   - Adds indexes for performance
   - Sets up sequences for IDs

**Testing**:
```bash
# Run migrations locally
docker-compose up
alembic upgrade head
# Verify tables in postgres:
psql -h localhost -U kalo_user -d kalo -c "\dt"
```

**Acceptance Criteria**:
- [ ] All 18 tables exist in PostgreSQL
- [ ] All foreign key relationships work
- [ ] `docker-compose up` completes without errors
- [ ] `curl http://localhost:8000/health` returns 200

---

### Priority 1.2: Error Handling & Validation
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Production apps need proper error handling
**Time**: 4-6 hours
**Difficulty**: Medium

**Files to Update**:
- `kalo-backend/app/api/auth.py` - Add 400/401/500 responses
- `kalo-backend/app/api/users.py` - Add 404/403/500 responses
- `kalo-backend/app/api/recipes.py` - Add validation, pagination errors
- All other API files similarly

**What to Add**:
```python
# Add Pydantic validation models
class CreateRecipeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    instructions: str = Field(..., min_length=10)
    servings: int = Field(..., gt=0, le=100)
    prep_time: int = Field(..., gt=0)

# Add HTTPException handling
@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

# Add try-except for database errors
try:
    db.add(new_recipe)
    await db.commit()
except IntegrityError:
    await db.rollback()
    raise HTTPException(status_code=400, detail="Recipe with this name exists")
except Exception as e:
    await db.rollback()
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Acceptance Criteria**:
- [ ] All endpoints return appropriate HTTP status codes
- [ ] Input validation with Pydantic
- [ ] Database errors handled gracefully
- [ ] 500 errors logged but don't crash server
- [ ] Rate limit responses (429)
- [ ] Authentication errors (401, 403)

---

### Priority 1.3: Environment Variables in iOS
**Status**: ⚠️ PARTIALLY STARTED
**Impact**: MEDIUM - iOS needs to know backend URL
**Time**: 30 minutes
**Difficulty**: Easy

**Files to Update**:
- `kalo/kalo/kalo/Services/NetworkingService.swift`
- Create `kalo/kalo/kalo/Config/APIConfig.swift`

**What to Add**:
```swift
// Config/APIConfig.swift
struct APIConfig {
    #if DEBUG
    static let baseURL = "http://localhost:8000"
    #else
    static let baseURL = "https://api.kalo.app"  // Production URL
    #endif
    
    static let timeout: TimeInterval = 30
    static let retryCount = 3
}

// In NetworkingService
private let baseURL = APIConfig.baseURL

// Usage in Views
let response = try await NetworkingService.request(
    endpoint: "/recipes",
    method: "GET",
    token: accessToken
)
```

**Acceptance Criteria**:
- [ ] iOS connects to localhost:8000 in development
- [ ] iOS connects to production API when released
- [ ] No hardcoded URLs in views
- [ ] Easy to switch between dev/prod

---

### Priority 1.4: Token Refresh Middleware
**Status**: ⚠️ PARTIAL
**Impact**: MEDIUM - App crashes on token expiry without refresh
**Time**: 1 hour
**Difficulty**: Medium

**Files to Update**:
- `kalo/kalo/kalo/Services/NetworkingService.swift`

**What to Add**:
```swift
// In NetworkingService
private func handleUnauthorized() async {
    // When 401 received:
    guard let refreshToken = KeychainHelper.refreshToken else {
        // No refresh token, logout user
        DispatchQueue.main.async {
            AuthViewModel.shared.logout()
        }
        return
    }
    
    // Try to refresh
    let newTokens = try? await refreshAccessToken(refreshToken)
    
    if let tokens = newTokens {
        // Store new tokens and retry request
        KeychainHelper.accessToken = tokens.accessToken
        KeychainHelper.refreshToken = tokens.refreshToken
        // Retry original request
    } else {
        // Refresh failed, logout
        await MainActor.run {
            AuthViewModel.shared.logout()
        }
    }
}

// Implement token refresh endpoint
private func refreshAccessToken(_ refreshToken: String) async throws -> TokenResponse {
    let url = URL(string: "\(baseURL)/auth/refresh")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("Bearer \(refreshToken)", forHTTPHeaderField: "Authorization")
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
        throw NetworkError.tokenRefreshFailed
    }
    
    return try JSONDecoder().decode(TokenResponse.self, from: data)
}
```

**Acceptance Criteria**:
- [ ] Token automatically refreshes before expiry
- [ ] User stays logged in for 7 days (refresh token duration)
- [ ] Graceful logout when refresh fails
- [ ] No manual re-login needed until refresh token expires

---

## 📱 Phase 2: iOS Features (2-3 weeks)

### Priority 2.1: GPS Running Tracker
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Differentiating feature, complex
**Time**: 6-8 hours
**Difficulty**: Hard (MapKit + CoreLocation + real-time)

**Files to Create**:
- `kalo/kalo/kalo/Views/Workouts/RunTrackerView.swift`
- `kalo/kalo/kalo/ViewModels/RunTrackerViewModel.swift`
- `kalo/kalo/kalo/Models/GPSCoordinates.swift` (already in AIModels)

**Architecture**:
```swift
// RunTrackerViewModel
@Observable
class RunTrackerViewModel {
    @MainActor
    var isRunning = false
    @MainActor
    var currentDistance: Double = 0
    @MainActor
    var pace: String = "0:00"  // min:sec per km
    @MainActor
    var coordinates: [GPSCoordinate] = []
    @MainActor
    var currentLocation: CLLocationCoordinate2D?
    @MainActor
    var elevation: Double = 0
    
    let locationManager = CLLocationManager()
    
    func startRun() {
        isRunning = true
        locationManager.startUpdatingLocation()
        locationManager.startUpdatingHeading()
    }
    
    func endRun() async throws {
        isRunning = false
        locationManager.stopUpdatingLocation()
        
        let run = Run(
            userId: currentUser.id,
            startTime: startTime,
            endTime: Date(),
            distance: currentDistance,
            pace: pace,
            elevation: elevation,
            coordinates: coordinates
        )
        
        try await NetworkingService.post("/runs", body: run)
    }
}

// RunTrackerView
struct RunTrackerView: View {
    @State var vm = RunTrackerViewModel()
    @State var mapPosition: MapCameraPosition = .userLocation(fallback: .automatic)
    
    var body: some View {
        ZStack {
            // Map with running route
            Map(position: $mapPosition) {
                UserAnnotation()
                
                // Draw polyline of route
                MapPolyline(coordinates: vm.coordinates.map { $0.coordinate })
                    .stroke(.blue, lineWidth: 3)
            }
            
            VStack {
                // Stats overlay
                StatsCard(
                    distance: vm.currentDistance,
                    pace: vm.pace,
                    elevation: vm.elevation
                )
                
                Spacer()
                
                // Start/Stop button
                Button(action: {
                    if vm.isRunning {
                        Task { try await vm.endRun() }
                    } else {
                        vm.startRun()
                    }
                }) {
                    Text(vm.isRunning ? "Stop Run" : "Start Run")
                }
            }
        }
        .onAppear {
            vm.locationManager.requestWhenInUseAuthorization()
        }
    }
}
```

**Acceptance Criteria**:
- [ ] User can start/stop running session
- [ ] GPS coordinates captured every second
- [ ] Distance calculated from coordinates
- [ ] Pace displayed (min:sec per km)
- [ ] Elevation tracked from altitude
- [ ] Map shows running route
- [ ] Run saved to backend on completion
- [ ] Runs appear in history

---

### Priority 2.2: Social Feed UI
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Engagement driver
**Time**: 4-6 hours
**Difficulty**: Medium

**Files to Create**:
- `kalo/kalo/kalo/Views/Social/SocialFeedView.swift`
- `kalo/kalo/kalo/ViewModels/SocialViewModel.swift`

**Key Features**:
- Vertical scrolling feed
- Post cards with images
- Like + comment buttons
- User profile link
- Pull to refresh

**Acceptance Criteria**:
- [ ] Posts load in infinite scroll
- [ ] Like/unlike works smoothly
- [ ] Comment creation works
- [ ] Pull to refresh updates feed
- [ ] Images load with caching
- [ ] Share button works

---

### Priority 2.3: Health Challenges UI
**Status**: ❌ NOT STARTED
**Impact**: MEDIUM - Engagement feature
**Time**: 3-4 hours
**Difficulty**: Medium

**Files to Create**:
- `kalo/kalo/kalo/Views/Challenges/ChallengesListView.swift`
- `kalo/kalo/kalo/Views/Challenges/ChallengeDetailView.swift`
- `kalo/kalo/kalo/ViewModels/ChallengesViewModel.swift`

**Key Features**:
- Browse available challenges
- Join challenge
- View leaderboard
- Submit proof (photo/GPS/data)
- Track progress

**Acceptance Criteria**:
- [ ] List challenges with filters
- [ ] Join challenge with one tap
- [ ] View other participants
- [ ] Upload proof photos
- [ ] See ranking on leaderboard

---

### Priority 2.4: Creator Marketplace UI
**Status**: ❌ NOT STARTED
**Impact**: LOW-MEDIUM - Revenue feature
**Time**: 4-5 hours
**Difficulty**: Medium

**Key Features**:
- Browse creator products
- Filter by type
- Add to cart
- Purchase
- Download/access content

---

## 🔧 Phase 3: Backend Enhancements (1-2 weeks)

### Priority 3.1: S3 Media Upload Handler
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Media storage essential
**Time**: 3-4 hours
**Difficulty**: Medium

**Files to Create**:
- `kalo-backend/app/services/media_service.py`

**What to Add**:
```python
# app/services/media_service.py
import aioboto3
from PIL import Image
import io

class MediaService:
    @staticmethod
    async def upload_image(file: UploadFile, path: str) -> str:
        # Optimize image (resize, compress)
        image = Image.open(file.file)
        image.thumbnail((1920, 1080))
        
        # Save to buffer
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        # Upload to S3
        async with aioboto3.client('s3') as s3_client:
            await s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=f"{path}/{file.filename}",
                Body=buffer,
                ContentType="image/jpeg",
                CacheControl="max-age=31536000"
            )
        
        # Return CloudFront URL
        return f"https://cdn.kalo.app/{path}/{file.filename}"
    
    @staticmethod
    async def upload_video(file: UploadFile, path: str) -> str:
        # Queue for transcoding with Celery
        task_id = transcode_video.delay(
            s3_key=f"{path}/{file.filename}"
        )
        return task_id
```

**Acceptance Criteria**:
- [ ] Images upload to S3
- [ ] Images optimized (resize + compress)
- [ ] Videos queued for transcoding
- [ ] CloudFront URLs returned
- [ ] CORS configured for uploads

---

### Priority 3.2: Celery Background Tasks
**Status**: ❌ NOT STARTED
**Impact**: HIGH - Long-running tasks need background processing
**Time**: 2-3 hours
**Difficulty**: Medium

**Files to Create**:
- `kalo-backend/app/tasks.py`

**What to Add**:
```python
# app/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_video_recipe(video_url: str, recipe_id: int):
    """Extract recipe from video in background"""
    try:
        pipeline = RecipeExtractionPipeline()
        recipe_data = asyncio.run(
            pipeline.extract_recipe_from_video(video_url)
        )
        
        # Save to database
        db.query(Recipe).filter(Recipe.id == recipe_id).update(recipe_data)
        db.commit()
        
        logger.info(f"Recipe {recipe_id} processed successfully")
    except Exception as e:
        logger.error(f"Recipe processing failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60)

@shared_task
def send_email_notification(user_id: int, subject: str, body: str):
    """Send email asynchronously"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Send email via SMTP
    send_email(
        to=user.email,
        subject=subject,
        body=body
    )

@shared_task
def generate_daily_analytics():
    """Generate daily user analytics"""
    users = db.query(User).all()
    for user in users:
        analytics = calculate_daily_stats(user.id)
        db.add(UserAnalytics(**analytics))
    db.commit()
```

**Update API to use Celery**:
```python
# In /app/api/recipes.py
@router.post("/extract-video")
async def extract_recipe_from_video(video_url: str, db: AsyncSession):
    recipe = Recipe(
        name="Processing...",
        user_id=current_user.id,
        status="processing"
    )
    db.add(recipe)
    await db.commit()
    
    # Queue task
    process_video_recipe.delay(video_url, recipe.id)
    
    return {"recipe_id": recipe.id, "status": "processing"}
```

**Acceptance Criteria**:
- [ ] Video recipes processed in background
- [ ] Celery worker running in docker-compose
- [ ] Tasks retry on failure
- [ ] User can check progress
- [ ] Emails sent asynchronously

---

### Priority 3.3: Rate Limiting
**Status**: ❌ NOT STARTED
**Impact**: MEDIUM - Prevent abuse
**Time**: 1-2 hours
**Difficulty**: Easy

**Files to Create**:
- `kalo-backend/app/middleware/rate_limit.py`

**What to Add**:
```python
# app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# In main.py
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.get("/recipes")
@limiter.limit("100/minute")
async def list_recipes(request: Request):
    ...

@router.post("/auth/login")
@limiter.limit("5/minute")  # Stricter limit for auth
async def login(request: Request):
    ...
```

**Acceptance Criteria**:
- [ ] 100 requests per minute for most endpoints
- [ ] 5 requests per minute for auth endpoints
- [ ] 429 response when exceeded
- [ ] Rate limit headers in response
- [ ] Redis-backed for distributed rate limiting

---

## 🧪 Phase 4: Testing & Monitoring (1-2 weeks)

### Priority 4.1: Backend Unit Tests
**Status**: ❌ NOT STARTED
**Impact**: MEDIUM - Catch regressions
**Time**: 4-6 hours
**Difficulty**: Medium

**Files to Create**:
- `kalo-backend/tests/test_auth.py`
- `kalo-backend/tests/test_recipes.py`
- `kalo-backend/tests/test_ai.py`
- etc.

**Example**:
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    response = await client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
```

**Acceptance Criteria**:
- [ ] 80%+ code coverage
- [ ] All critical paths tested
- [ ] Tests run in CI/CD
- [ ] Failing tests block deploy

---

### Priority 4.2: Monitoring & Logging
**Status**: ❌ NOT STARTED
**Impact**: MEDIUM - Essential for production
**Time**: 2-3 hours
**Difficulty**: Medium

**Tools to Add**:
- Sentry for error tracking
- DataDog or New Relic for APM
- CloudWatch or ELK for logs

**What to Add**:
```python
# In main.py
import sentry_sdk

if settings.ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT
    )

# Structured logging
import structlog
logger = structlog.get_logger()

# In API handlers
logger.info(
    "recipe_created",
    recipe_id=recipe.id,
    user_id=current_user.id,
    macros=recipe.macros
)
```

**Acceptance Criteria**:
- [ ] All errors logged with context
- [ ] Performance metrics tracked
- [ ] Alerts on critical errors
- [ ] 30-day log retention

---

## 🚀 Phase 5: Production Deployment (1 week)

### Priority 5.1: Deploy Backend to Railway
**Impact**: HIGH - Must be live
**Time**: 2-3 hours
**Difficulty**: Easy

**Steps**:
1. Connect GitHub repo to Railway
2. Create PostgreSQL database in Railway
3. Create Redis instance
4. Set environment variables
5. Deploy → Get production URL

**See `DEPLOYMENT.md` for detailed steps**

**Acceptance Criteria**:
- [ ] Backend live at api.kalo.app
- [ ] All endpoints respond
- [ ] Database persists data
- [ ] Background jobs work

---

### Priority 5.2: Deploy iOS to App Store
**Impact**: HIGH - Users need to download
**Time**: 4-6 hours
**Difficulty**: Medium (depends on App Store review)

**Steps**:
1. Update build number + version in Xcode
2. Create App Store Connect listing
3. Configure app capabilities
4. Upload build to TestFlight
5. Invite testers
6. Submit for review
7. App Store publishes after approval

**Acceptance Criteria**:
- [ ] App available on App Store
- [ ] Installs on real iPhone
- [ ] Connects to production backend
- [ ] All features work end-to-end

---

## 📊 Overall Timeline

```
Week 1:  Database Migrations + Error Handling + Token Refresh
         ├─ Monday: Alembic migrations (3h) + Error handling (4h)
         ├─ Tuesday: Token refresh (2h) + iOS config (1h)
         ├─ Wednesday: Testing + debugging
         ├─ Thursday: Verify backend ready for iOS
         └─ Friday: Buffer / Optimization

Week 2-3: iOS Features
         ├─ GPS Running Tracker (8h)
         ├─ Social Feed UI (6h)
         ├─ Challenges UI (4h)
         ├─ Testing + debugging
         └─ iOS TestFlight build

Week 3-4: Backend Enhancements
         ├─ S3 Media Upload (4h)
         ├─ Celery Background Tasks (3h)
         ├─ Rate Limiting (2h)
         ├─ Unit Tests (6h)
         ├─ Monitoring + Logging (3h)
         └─ Load testing

Week 4-5: Production Deployment
         ├─ Railway deployment
         ├─ Database migration production
         ├─ App Store submission
         ├─ User testing
         └─ Launch!

Total: 4-5 weeks to full production
```

---

## ✅ Success Criteria

**Before Production Launch**:
- [ ] Backend runs locally without errors
- [ ] iOS app compiles and installs on simulator
- [ ] End-to-end test: signup → meal plan → save → verify in database
- [ ] All 10 API endpoints return correct responses
- [ ] Database migrations tested locally
- [ ] Error handling for all failure cases
- [ ] Token refresh works automatically
- [ ] Rate limiting prevents abuse
- [ ] Logging structured + searchable
- [ ] Monitoring alerts configured

**For MVP Success**:
- [ ] 100+ test users
- [ ] Average session 15+ minutes
- [ ] 50%+ day-2 retention
- [ ] <2s API response time
- [ ] <1% error rate
- [ ] Zero data loss events

---

## 🎯 Decision Points

### Which iOS feature first?
**Recommendation**: GPS Runner (highest differentiation)
- Most technically complex (forces good architecture)
- Most novel (differentiates from competitors)
- Best engagement signal (users track workouts)
- Alternative: Social Feed (simpler, faster engagement)

### Database: PostgreSQL or managed?
**Recommendation**: AWS RDS or Railway managed
- Less operational overhead
- Automatic backups + failover
- Scaling handled automatically
- Cheaper than self-managed at scale

### AI: Run locally or use API?
**Recommendation**: Use OpenAI API + local inference for faster iteration
- No GPU needed locally
- Easy to swap models later
- OpenAI handles model updates
- Costs scale with usage (good for MVP)

### Deployment: Railway or AWS?
**Recommendation**: Railway for speed, AWS for scale
- Railway: Deploy in <5 minutes, easier for startup
- AWS: More control, better for enterprise customers
- Consider Railway → AWS migration path

---

## 💡 Pro Tips

1. **Test locally before deploying**: `docker-compose up` + `pytest`
2. **Keep environment configs separate**: Never commit .env
3. **Use database transactions**: Prevent partial updates on errors
4. **Add request/response logging**: Save 10 minutes debugging per incident
5. **Build mobile-first**: Constraint drives better design
6. **Monitor API latency**: <200ms for smooth UX
7. **Cache aggressively**: Redis for hot data (user preferences, top recipes)
8. **Batch database operations**: Reduces query count dramatically
9. **Rate limit early**: Better to throttle than crash
10. **Gather analytics**: Understand what users actually do vs. what you think

---

## 📞 Quick Support

**Backend won't start?**
- Check ports: `lsof -i :8000`
- Check docker: `docker ps`
- View logs: `docker-compose logs -f`

**iOS won't compile?**
- Clean: `Cmd+Shift+K`
- Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData/*`
- Rebuild: `Cmd+B`

**API returns 500?**
- Check logs: `docker-compose logs backend`
- Verify .env variables
- Test with curl: `curl http://localhost:8000/health`

**iOS can't connect to backend?**
- Verify backend running: `curl http://localhost:8000/health`
- Check Info.plist for App Transport Security
- Verify URL in Config/APIConfig.swift
- Check proxy settings

---

**Next Action**: Start with Priority 1.1 (Database Migrations)
**Estimated Time to MVP**: 4-5 weeks from now
**Estimated Time to Scale-Ready**: 8-10 weeks total

Good luck! 🚀
