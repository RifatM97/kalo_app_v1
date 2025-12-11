# 🥗 Kalo - iOS Nutrition & Fitness App

A beautiful, modern SwiftUI-based iPhone app for tracking nutrition, recipes, meal planning, grocery lists, and workouts. Built with a mint-green theme following Apple's Human Interface Guidelines.

## 📋 Project Structure

```
kalo/
├── Models/                      # Data models
│   ├── User.swift              # Authentication & user data
│   ├── Recipe.swift            # Recipe model with ingredients & macros
│   ├── Ingredient.swift        # Individual ingredients
│   ├── Macro.swift             # Macro tracking (protein, carbs, fat)
│   ├── PlannerDay.swift        # Weekly meal planning
│   └── Workout.swift           # Workout logging
│
├── ViewModels/                  # State management (@Observable)
│   ├── AuthViewModel.swift      # Login/Signup
│   ├── HomeViewModel.swift      # Daily summary & stats
│   ├── RecipeViewModel.swift    # Recipe management
│   ├── ImportRecipeViewModel.swift  # URL extraction
│   ├── PlannerViewModel.swift   # Meal planning
│   ├── GroceryViewModel.swift   # Grocery list
│   └── WorkoutViewModel.swift   # Workout tracking
│
├── Views/                       # SwiftUI screens
│   ├── RootView.swift          # Navigation hub
│   ├── TabRootView.swift       # Tab bar navigation
│   ├── Auth/
│   │   ├── LoginView.swift
│   │   └── SignupView.swift
│   ├── Home/
│   │   └── HomeView.swift      # Daily dashboard
│   ├── Recipes/
│   │   ├── RecipeListView.swift
│   │   ├── RecipeDetailView.swift
│   │   └── ImportRecipeView.swift
│   ├── Planner/
│   │   └── PlannerView.swift   # Weekly meal planner
│   ├── Grocery/
│   │   └── GroceryView.swift   # Auto-generated lists
│   ├── Workouts/
│   │   └── WorkoutView.swift   # Exercise logging
│   └── Components/
│       ├── KaloButton.swift    # Mint-themed buttons
│       └── CardModifier.swift  # Reusable card styling
│
├── Services/                    # Networking & storage
│   ├── NetworkingService.swift # async/await API calls
│   └── KeychainHelper.swift    # Secure token storage
│
├── Extensions/
│   └── Color+Kalo.swift        # Theme colors
│
├── Config.swift                # API URLs, theme constants
├── KaloApp.swift               # App entry point
└── kalo.entitlements          # App entitlements
```

## 🎨 Design System

### Colors
- **Primary (Mint)**: `#4BE3C1` (RGB: 75, 227, 193)
- **Background**: Pure White `#FFFFFF`
- **Text**: Dark Gray `#1A1A1A`
- **Dividers**: Light Gray `#ECECEC`

### Typography
- **Headlines**: System font, bold, weight .bold
- **Body**: System font, weight .medium
- **Captions**: System font 12-13pt, weight .medium

### Components
- **Buttons**: Rounded 12pt, mint background, white text
- **Cards**: Rounded 16pt, white background, subtle shadows
- **Spacing**: 16pt standard padding

## 🚀 Getting Started

### Prerequisites
- **Xcode**: 15.0 or later
- **iOS**: 16.0 minimum
- **macOS**: For running the simulator

### Installation & Running

1. **Clone the repository**
   ```bash
   cd /Users/arafathossain/Documents/kalo/kalo
   ```

2. **Open in Xcode**
   ```bash
   open kalo.xcodeproj
   ```

3. **Select Target & Simulator**
   - Target: `kalo`
   - Simulator: iPhone 15 Pro (or any iPhone 14+)

4. **Build & Run**
   - Press `Cmd + R` or click the Play button
   - Or use terminal:
     ```bash
     xcodebuild -scheme kalo -derivedDataPath ./build -destination 'generic/platform=iOS Simulator' build
     ```

5. **Test the App**
   - **Splash Screen**: Shows login/signup options
   - **Login**: Use any email/password (mock auth)
   - **Home Tab**: Daily calorie & macro summary
   - **Recipes Tab**: View, import, and save recipes
   - **Planner Tab**: Plan meals for the week
   - **Grocery Tab**: Auto-generated from planner
   - **Workouts Tab**: Log exercises with sets/reps/weight

## 🔐 Authentication

The app uses **JWT tokens stored in Keychain** for secure authentication.

### Mock Login Credentials
- Email: Any email address (e.g., `user@example.com`)
- Password: Any password (mock auth doesn't validate)

**In Production**, replace mock methods in `AuthViewModel.signup()` and `AuthViewModel.login()` with actual API calls to your backend:

```swift
let response = try await networkService.request(
    "/auth/login",
    method: "POST",
    body: request,
    as: AuthResponse.self
)
keychainHelper.saveToken(response.token)
```

## 🔌 API Integration

### NetworkingService

All API calls use **async/await** with automatic JWT token injection:

```swift
// Example: POST request
let response = try await NetworkingService.shared.request(
    "/recipes/save",
    method: "POST",
    body: recipe,
    as: Recipe.self
)
```

### Base URL Configuration

Edit `Config.swift`:

```swift
static let baseURL = URL(string: "http://localhost:8000")!
static let apiPrefix = "/api/v1"
```

### Example Backend Endpoints

```
POST   /api/v1/auth/login           # Login
POST   /api/v1/auth/signup          # Create account
POST   /api/v1/recipes/extract      # Extract from URL
GET    /api/v1/recipes              # List recipes
POST   /api/v1/recipes              # Save recipe
GET    /api/v1/planner              # Get meal plan
POST   /api/v1/planner/update       # Update meal plan
GET    /api/v1/workouts             # Get workouts
POST   /api/v1/workouts             # Log workout
```

## 📱 Features

### ✅ Implemented
- [x] Authentication (Mock + Real token storage)
- [x] Home dashboard with calorie/macro tracking
- [x] Recipe library with search
- [x] Import recipes from URLs (mock extraction)
- [x] Weekly meal planner with drag-drop
- [x] Auto-generated grocery lists
- [x] Workout logger with sets/reps/weight
- [x] Mint-themed UI following iOS design patterns
- [x] Tab-based navigation
- [x] Keychain secure storage

### 🔄 Future Enhancements
- Real backend API integration
- SwiftData local persistence
- Recipe photos from camera/gallery
- Barcode scanning for groceries
- Apple Health integration
- Notifications for meal reminders
- Social sharing of recipes
- Advanced analytics & trends

## 🛠️ Architecture

### MVVM + @Observable

The app uses Swift's new `@Observable` macro (iOS 17+) for state management:

```swift
@Observable
final class RecipeViewModel {
    var recipes: [Recipe] = []
    
    func loadRecipes() async {
        // Fetch from API
    }
}
```

### Dependency Injection

Views receive ViewModels as `@State`:

```swift
struct HomeView: View {
    @State var homeVM: HomeViewModel
}
```

## 🧪 Testing

### Preview in Xcode
Every view has a `#Preview` block for quick testing:

```swift
#Preview {
    HomeView(homeVM: HomeViewModel())
}
```

### Run Unit Tests
```bash
xcodebuild -scheme kaloTests -derivedDataPath ./build test
```

## 📦 Dependencies

**Built-in frameworks only:**
- SwiftUI
- Foundation
- Combine
- URLSession
- Security (Keychain)

**No external CocoaPods or SPM packages required!**

## 🎯 App Flow

```
SplashView (Auth Check)
    ↓
LoginView / SignupView
    ↓
    ↓ (Authenticated)
TabRootView
├─ HomeView (Daily Dashboard)
├─ RecipeListView (Browse & Search)
│   └─ RecipeDetailView
│   └─ ImportRecipeView (URL Extraction)
├─ PlannerView (Weekly Meals)
├─ GroceryView (Auto-Generated List)
└─ WorkoutView (Exercise Logger)
```

## 🚨 Common Issues & Solutions

### Issue: "Cannot find Xcode scheme"
**Solution**: Make sure the `kalo` scheme is selected in Product → Scheme

### Issue: Simulator doesn't load the app
**Solution**: 
1. Product → Clean Build Folder (`Cmd + Shift + K`)
2. Delete Derived Data: `rm -rf ~/Library/Developer/Xcode/DerivedData/*`
3. Rebuild and run

### Issue: Keychain errors in simulator
**Solution**: Simulator keychain is reset on each clean. This is normal. Manually enter credentials again.

### Issue: SwiftUI previews not rendering
**Solution**: Ensure `#Preview` macro is used (not old `PreviewProvider`)

## 📚 Resources

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/ios)
- [@Observable Macro](https://developer.apple.com/documentation/observation)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)

## 📄 License

This is a demo/educational project. Feel free to use and modify for your needs.

---

**Built with ❤️ using SwiftUI**

Questions? Check the code comments or review the ViewModels for logic examples.
