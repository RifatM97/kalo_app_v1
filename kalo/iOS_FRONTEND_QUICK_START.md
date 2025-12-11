# 🚀 KALO FRONTEND - QUICK START GUIDE

## Files Created (5 New Components)

### 1. `Views/Home/HomeHeader.swift`
**What**: Greeting header with user name and date  
**Key Components**:
- Time-based greeting ("Good morning/afternoon/evening")
- User avatar placeholder (44×44 circle)
- Current date display
- Integration point: TODO - connect to actual User model

**Usage**:
```swift
HomeHeader()  // Drop into any view
```

### 2. `Views/Home/TodayPlanSection.swift`
**What**: Display today's 3 meals (Breakfast, Lunch, Dinner)  
**Key Components**:
- `MealCard` subcomponent for individual meals
- Shows meal name, calories, scheduled time, icon

**Usage**:
```swift
TodayPlanSection()  // Shows all 3 meals
```

### 3. `Views/Home/RecipesCarousel.swift`
**What**: Horizontal scrolling carousel of saved recipes  
**Key Components**:
- `RecipeCardCompact` subcomponent
- 5 recipe cards visible (swipe for more)
- "See All" navigation link

**Usage**:
```swift
RecipesCarousel()  // Horizontal scroll of recipes
```

### 4. `Views/Home/WorkoutChallengesSection.swift`
**What**: Active workouts and challenges with progress  
**Key Components**:
- `WorkoutCard` for upcoming workouts
- `ChallengeCard` for active challenges with progress bar
- Workout duration/distance, challenge day counter

**Usage**:
```swift
WorkoutChallengesSection()  // Shows workouts + challenges
```

### 5. `Views/Home/ChatBottomSheetView.swift`
**What**: Modal chat interface that slides up from bottom  
**Key Components**:
- Integrates existing `AIChatView` and `AIChatViewModel`
- Drag handle, close button, dimming background
- Message bubbles, input field, send button

**Usage**:
```swift
@State private var showChat = false

ChatBottomSheetView(isPresented: $showChat)  // Conditional presentation
```

---

## Files Modified (2 Updates)

### 1. `Views/Home/HomeView.swift`
**Changes**:
- Replaced `HeaderSection` with new `HomeHeader` component
- Added all 4 new section components in order
- Added `ChatPillButton` at bottom to open chat modal
- Updated background color to `systemGray6`
- Added state management for chat modal

**New Layout**:
```
HomeHeader
├─ CalorieSummaryCard (existing)
├─ QuickActionsSection (existing)
├─ TodayPlanSection (NEW)
├─ RecipesCarousel (NEW)
├─ WorkoutChallengesSection (NEW)
└─ ChatPillButton (NEW)
   └─ Opens ChatBottomSheetView on tap
```

### 2. `Views/TabRootView.swift`
**Changes**:
- ✅ REMOVED: "AI Chat" tab (was index 4)
- ✅ KEPT: 5 tabs (Home, Recipes, Planner, Grocery, Workouts)
- Removed unused `aiChatVM` state variable
- Chat now accessed via Home screen pill button

**Tab Order**:
```
0: Home       (includes chat modal)
1: Recipes
2: Planner
3: Grocery
4: Workouts   (was 5, now 4)
```

---

## Key Design Patterns

### Apple App Store Inspired
- ✅ Large, bold section titles
- ✅ Generous spacing and white space
- ✅ Cards with soft rounded corners (12-20px)
- ✅ Subtle shadows (opacity 0.05)
- ✅ Clean icons (SF Symbols)

### iOS-Native Feel
- ✅ SwiftUI native components
- ✅ System colors (Color.white, systemGray6)
- ✅ Safe area respect
- ✅ Smooth animations (easeInOut)
- ✅ iMessage-style chat bubbles

### Kalo Branding
- ✅ Mint primary color (#4BE3C1)
- ✅ White cards and backgrounds
- ✅ SF Pro typography
- ✅ Consistent 16px padding
- ✅ Mint + white color scheme

---

## Integration Checklist

### Before Building
- [ ] Run `xcode-build` to verify syntax
- [ ] Check for any missing imports
- [ ] Verify all custom components compile

### Configuration
- [ ] Update `User` model in `HomeHeader` (currently hardcoded "Rifat")
- [ ] Connect real meal data from `HomeViewModel` to `TodayPlanSection`
- [ ] Connect real recipes from `RecipeViewModel` to `RecipesCarousel`
- [ ] Connect real workout data to `WorkoutChallengesSection`

### Testing
- [ ] Test on iPhone 12 simulator
- [ ] Test on iPhone 14 simulator
- [ ] Test on iPhone SE (375px)
- [ ] Test landscape orientation
- [ ] Test chat modal open/close
- [ ] Test message sending/receiving
- [ ] Verify no layout breaks on landscape

### Production Checklist
- [ ] Verify all NavigationLinks navigate correctly
- [ ] Test on actual device
- [ ] Performance test (scroll smoothness)
- [ ] Dark mode support (optional)
- [ ] Accessibility audit (VoiceOver)

---

## State Management

### HomeView States
```swift
@State private var showImportSheet = false      // Existing
@State private var showChatBottomSheet = false   // NEW - controls chat modal
```

### ChatBottomSheetView States
```swift
@State private var aiChatVM = AIChatViewModel()  // Local chat instance
@FocusState private var isInputFocused: Bool     // Input field focus
```

### Notes
- Chat uses its own local `AIChatViewModel` instance
- Messages persist within that session
- Closing sheet doesn't clear messages (they persist on reopen)
- To clear messages, use "refresh" button in chat header

---

## Styling Reference

### Colors
```swift
KaloTheme.mint           // Primary: #4BE3C1
KaloTheme.text           // Text: #1A1A1A (black)
KaloTheme.divider        // Divider: #EEEEEE (light gray)
Color.white              // Card backgrounds
Color(UIColor.systemGray6)  // Section backgrounds
```

### Spacing
```swift
KaloTheme.padding = 16    // Standard margin
Section spacing: 20       // Between major sections
Card padding: 12-16       // Inside cards
Item spacing: 12          // Between items in stack
```

### Corner Radius
```swift
20 - Sheet (top corners only)
16 - Chat pill, Header
14 - Recipe cards
12 - Meal cards, small containers
```

### Shadows
```swift
Color.black.opacity(0.05)  // Shadow color
Radius: 8                  // Blur radius
Offset: (0, 2)            // Subtle drop shadow
```

---

## Code Examples

### Opening Chat Modal
```swift
@State private var showChat = false

Button("Chat") {
    withAnimation(.easeInOut(duration: 0.3)) {
        showChat = true
    }
}

ChatBottomSheetView(isPresented: $showChat)
```

### Adding a New Section
```swift
VStack(alignment: .leading, spacing: 16) {
    // Section Title
    VStack(alignment: .leading, spacing: 4) {
        Text("Section Title")
            .font(.system(size: 18, weight: .semibold))
            .foregroundColor(KaloTheme.text)
        
        Text("Subtitle")
            .font(.system(size: 13, weight: .medium))
            .foregroundColor(.secondary)
    }
    
    // Content
    // ...
}
.frame(maxWidth: .infinity, alignment: .leading)
.padding(16)
.background(Color.white)
```

### Custom Card Styling
```swift
VStack {
    // Content
}
.padding(12)
.background(Color(UIColor.systemGray6))
.cornerRadius(12)
.shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 2)
```

---

## Troubleshooting

### Chat Modal Not Opening
- Check `@State` variable `showChatBottomSheet` is declared in HomeView
- Verify `ChatBottomSheetView` is in conditional `if` block
- Confirm animation closure uses `withAnimation`

### Chat Messages Not Appearing
- Check `AIChatViewModel` is initialized with state
- Verify backend `/api/ai/chat` endpoint is running
- Check network console for API errors

### Layout Breaking on Landscape
- Ensure all ScrollViews and VStacks use proper frame modifiers
- Test on `iPhone 14 Pro Max` landscape mode
- May need to add conditional `.ignoresSafeArea()` for landscape

### Performance Issues (Scroll Lag)
- Check recipe carousel doesn't have too many cards (limit to 5)
- Verify no complex animations in scrolling content
- Profile with Xcode Instruments (Debug → Profile)

---

## Next Steps

### Phase 6 (Styling Polish) - Current
- [ ] Fine-tune shadows and spacing
- [ ] Test on actual iPhone
- [ ] Verify smooth scrolling
- [ ] Optimize animations

### Phase 7 (Testing & Verification)
- [ ] Test all interactive elements
- [ ] Verify chat functionality
- [ ] Test across iPhone sizes
- [ ] Performance benchmarking

### Future Enhancements
- [ ] Connect to real User model (name, avatar)
- [ ] Pull real meal data from backend
- [ ] Show real recipe library
- [ ] Live workout status
- [ ] Challenge progress from database
- [ ] Dark mode support
- [ ] Streaming chat responses
- [ ] Voice message input
- [ ] Recipe detail view navigation

---

## Support & Documentation

**Visual Layout**: See `iOS_LAYOUT_WIREFRAME.md`  
**Implementation Details**: See `iOS_FRONTEND_REDESIGN_SUMMARY.md`  
**Backend API**: See `kalo-backend/LLM_SETUP_GUIDE.md`  
**Project Overview**: See `README_MASTER.md`  

---

**Status**: ✅ Ready for Testing & Integration  
**Last Updated**: December 7, 2025  
**Maintainer**: Kalo Frontend Team  
