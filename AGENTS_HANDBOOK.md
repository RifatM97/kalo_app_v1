# 🎯 KALO QUICK REFERENCE - AGENTS HANDBOOK

## 🚀 Getting Started (Right Now)

### 1️⃣ Start Backend
```bash
cd /Users/rifathossain/Desktop/kalo/kalo-backend
python main.py
# Should print: INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2️⃣ Verify It Works
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "service": "kalo-api", ...}
```

### 3️⃣ Open iOS Project
```bash
cd /Users/rifathossain/Desktop/kalo/kalo
open kalo.xcodeproj
# Cmd+B to build (should succeed with no warnings)
```

---

## 📚 Documentation Map

| Need | File | Use When |
|------|------|----------|
| Network issues | `NETWORK_SETUP_GUIDE.md` | "Can't connect to backend" |
| API contracts | `BACKEND_API_REFERENCE.md` | "What does this endpoint return?" |
| Implementation specs | `IMPLEMENTATION_ROADMAP.md` | "How do I build Phase 3-8?" |
| Big picture | `LEAD_AGENT_SUMMARY.md` | "What's the overall plan?" |
| This guide | (you are here) | Quick lookup |

---

## 🎓 Core Patterns to Use

### Making API Calls
```swift
// ✅ GOOD - Use NetworkingService
let runs = try await NetworkingService.shared.get(
    "runs",
    as: [Run].self
)

// ❌ WRONG - Don't make direct URLSession calls
// let url = URL(string: "http://localhost:8000/...")!
```

### Error Handling
```swift
// ✅ GOOD
do {
    let data = try await networkService.request(...)
} catch let error as NetworkError {
    if error.isNetworkUnavailable {
        // Show "Backend offline" message
    } else {
        // Show error.errorDescription
    }
}
```

### Colors & Styling
```swift
// ✅ GOOD - Use KaloTheme
.foregroundColor(KaloTheme.mint)
.background(KaloTheme.background)
.cornerRadius(KaloTheme.cardCornerRadius)

// ❌ WRONG - No hardcoded colors
// .foregroundColor(Color(red: 0.3, green: 0.9, blue: 0.75))
```

### Haptics
```swift
// ✅ GOOD - Use HapticsService
HapticsService.shared.impact(.medium)
HapticsService.shared.notification(.success)
HapticsService.shared.selection()

// ❌ WRONG - Don't use CHHapticPattern
// (causes plist errors on simulator)
```

---

## 🔧 Common Tasks

### Test API Endpoint (curl)
```bash
# GET with auth
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs

# POST with JSON
curl -X POST http://localhost:8000/api/runs/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Debug Network Issues
```swift
// Add this to any view temporarily
VStack {
    if let error = networkError {
        Text("Error: \(error)")
            .foregroundColor(.red)
    }
}
.onAppear {
    Task {
        do {
            let isConnected = try await NetworkingService.shared.checkConnectivity()
            print("Connected: \(isConnected)")
        } catch let error as NetworkError {
            networkError = error.errorDescription
        }
    }
}
```

### Test on Physical Device
1. Find your Mac IP: `ifconfig | grep "inet " | grep -v 127`
2. Update Config.swift:
   ```swift
   case .devRemote:
       return URL(string: "http://192.168.x.x:8000")!  // ← YOUR IP
   ```
3. Both Mac and iPhone on same WiFi
4. Build & run

---

## 🎯 Phase-Specific Quickstarts

### Phase 3: Workouts
**Files to create**:
1. `ViewModels/WorkoutViewModel.swift` - Fetch, cache workouts
2. `Views/Workouts/LogWorkoutView.swift` - Create new
3. `Views/Workouts/WorkoutHistoryView.swift` - List
4. `Views/Workouts/WorkoutDetailView.swift` - Detail + PR

**API Endpoints**:
```
POST   /api/workouts                 # Log new workout
GET    /api/workouts                 # List
GET    /api/workouts/{id}            # Detail
PUT    /api/workouts/{id}            # Update
```

**Key Features**:
- [ ] Personal Records (PR) detection
- [ ] Volume calculation (reps × weight)
- [ ] Exercise history

### Phase 4: Running
**Files to create**:
1. `ViewModels/RunTrackingViewModel.swift` - CoreLocation
2. `Views/Running/RunTrackingView.swift` - Live tracking
3. `Views/Running/RunDetailView.swift` - View completed
4. `Views/Running/RunShareCardView.swift` - Share image
5. `Models/RunTracking.swift` - Data models

**API Endpoints**:
```
POST   /api/runs/start                # Start session
POST   /api/runs/{id}/update          # Live tracking
POST   /api/runs/{id}/finish          # Complete
GET    /api/runs                      # History
GET    /api/runs/{id}                 # Detail
GET    /api/runs/summary/stats        # Stats
GET    /api/runs/heatmap/data         # Calendar
```

**Key Features**:
- [ ] Real-time CoreLocation tracking
- [ ] MapKit route visualization
- [ ] Branded share card (image generation)
- [ ] Pace & calories calculation

### Phase 5: Heatmap
**File to create**:
1. `Views/Activity/ActivityHeatmapView.swift`

**API Endpoint**:
```
GET    /api/runs/heatmap/data?period=week|month|year
```

**Key Features**:
- [ ] Calendar grid (7×6)
- [ ] Color intensity by distance
- [ ] Period selector (week/month/year)

### Phase 6: Social Feed
**Files to create**:
1. `ViewModels/SocialFeedViewModel.swift`
2. `Views/Social/SocialFeedView.swift` - Feed list
3. `Views/Social/PostCardView.swift` - Post cards
4. `Views/Social/CreatePostView.swift` - Compose
5. `Models/Post.swift` - Data models

**API Endpoints**:
```
GET    /api/posts/feed                # Get feed
POST   /api/posts                     # Create post
POST   /api/posts/{id}/like           # Like
POST   /api/posts/{id}/comment        # Comment
```

**Key Features**:
- [ ] Mixed post types (run, workout, meal)
- [ ] Like/comment actions
- [ ] Infinite scroll

---

## 🎨 Design System Quick Reference

```swift
// Colors
KaloTheme.mint              // #4BE3C1
KaloTheme.background        // White
KaloTheme.text              // #1A1A1A
KaloTheme.secondaryText     // Gray
KaloTheme.divider           // #ECECEC

// Sizes
KaloTheme.cardCornerRadius  // 16pt
KaloTheme.buttonCornerRadius // 12pt
KaloTheme.padding           // 16pt

// Shadows
KaloTheme.shadowColor       // black.opacity(0.08)
KaloTheme.shadowRadius      // 8pt
KaloTheme.shadowX           // 0
KaloTheme.shadowY           // 2pt
```

---

## ✅ Code Review Checklist

Every new file should have:

- [ ] Uses `NetworkingService` for API calls (not URLSession directly)
- [ ] Errors use `NetworkError` enum
- [ ] All UI colors from `KaloTheme` (no hardcoded colors)
- [ ] Spacing/corner radius from `KaloTheme`
- [ ] Loading state (`@State var isLoading = false`)
- [ ] Error state with user-friendly message
- [ ] Haptics feedback on key actions (HapticsService)
- [ ] Proper async/await (no .done or blocking)
- [ ] View models with @Published properties
- [ ] Models are Codable (for API serialization)
- [ ] No force unwraps (`!`) in production code
- [ ] Comments for non-obvious logic

---

## 🆘 Troubleshooting

### "Connection refused"
1. Is backend running? Check: `curl http://localhost:8000/health`
2. Wrong port? Verify main.py line 117: `port=8000`
3. On device? Update Config.swift to use your Mac IP

### "Cannot decode response"
1. Check model matches API response
2. Use `JSONDecoder()` with proper CodingKeys
3. Print API response: `print(String(data: data, encoding: .utf8))`

### "Haptics console error"
1. Don't use `CHHapticPattern` directly
2. Use `HapticsService.shared.impact()` instead
3. Should work on simulator & device

### "Compilation errors"
1. Clean build: `Cmd+Shift+K`
2. Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData/*`
3. Rebuild: `Cmd+B`

---

## 📊 Progress Tracking

### Current Status
- **Phase 1**: ✅ COMPLETE
- **Phase 2**: ✅ COMPLETE
- **Phase 3**: ⏳ Ready (next)
- **Phase 4-8**: ⏳ In queue

### Estimated Timeline
- Phase 3 (Workouts): 6-8 hours
- Phase 4 (Running): 10-12 hours
- Phase 5 (Heatmap): 4-6 hours
- Phase 6 (Social): 8-10 hours
- Phase 7 (Design): 3-4 hours
- Phase 8 (Testing): 4-5 hours

**Total**: ~40-50 hours of implementation

---

## 🎁 Bonus: Copy-Paste Templates

### New ViewModel Template
```swift
import Foundation

@MainActor
class YourViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var error: String?
    @Published var data: [YourModel] = []
    
    private let networkService = NetworkingService.shared
    
    func fetch() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            data = try await networkService.get("your-endpoint", as: [YourModel].self)
            error = nil
        } catch let error as NetworkError {
            self.error = error.errorDescription
        } catch {
            self.error = "Unknown error"
        }
    }
}
```

### New View Template
```swift
import SwiftUI

struct YourView: View {
    @StateObject private var viewModel = YourViewModel()
    
    var body: some View {
        VStack(spacing: 16) {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                Text("Error: \(error)")
                    .foregroundColor(.red)
                    .padding()
            } else {
                List(viewModel.data) { item in
                    Text(item.title)
                }
            }
        }
        .onAppear { Task { await viewModel.fetch() } }
    }
}
```

---

## 📞 Final Checklist Before Starting Phase 3

- [ ] Read `IMPLEMENTATION_ROADMAP.md` for Phase 3 details
- [ ] Backend running: `python main.py`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] iOS compiles: `Cmd+B`
- [ ] Reviewed code patterns above
- [ ] Bookmarked API reference: `BACKEND_API_REFERENCE.md`
- [ ] Starred this file (it's your handbook!)

---

**You're ready. Let's build! 🚀**
