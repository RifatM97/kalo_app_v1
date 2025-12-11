# Kalo iOS App - Integration & Testing Guide

## Quick Start

### Build & Run

```bash
cd /Users/arafathossain/Documents/kalo/kalo
open kalo.xcodeproj
# Select Simulator (iPhone 15 Pro or similar)
# Press Cmd+R to build and run
```

### Expected Behavior

1. **App Launches** → Shows login screen (existing feature)
2. **After Login** → Shows 6-tab TabView:
   - Home (house icon)
   - Recipes (book icon)
   - Planner (calendar icon)
   - Grocery (cart icon)
   - **AI (sparkles icon)** ← NEW
   - Workouts (figure icon)

---

## Feature Testing

### 1. AI Chat Tab ✨

**Access:** Tap the "AI" tab (sparkles icon)

**What You See:**
- Header: "Kalo AI Assistant" with sparkles icon
- Clear button (top right)
- Chat area with messages
- Input field at bottom
- Send button

**To Test:**
1. Type "How many calories in a banana?"
2. Tap send button
3. Should show "typing indicator" (animated dots)
4. AI response appears in white bubble on left
5. Your messages appear in mint bubbles on right

**Backend Requirement:**
```
POST /ai/chat
{
  "message": "How many calories in a banana?"
}

Response:
{
  "reply": "A medium banana has about 105 calories..."
}
```

---

### 2. Barcode Scanner 📱

**Access:** Grocery tab → "Add Item" button → "Scan Barcode"

**What You See:**
- Camera view with crosshair
- Close button (top right)
- Device asks for camera permission (first time)

**To Test (Simulator):**
- In real Simulator, camera won't work
- Must test on physical device with actual barcode
- Or modify code to mock barcode results

**To Test (Physical Device):**
1. Go to Grocery → Add Item
2. Tap "Scan Barcode"
3. Grant camera permission if prompted
4. Point camera at product barcode (EAN-13, UPC-A, or UPC-E)
5. Barcode scans automatically
6. Returns to Add Item sheet
7. Product name auto-fills

**Backend Requirement:**
```
POST /nutrition/barcode
{
  "barcode": "5901234123457"
}

Response:
{
  "barcode": "5901234123457",
  "productName": "Whole Grain Bread",
  "calories": 265,
  "protein": 9,
  "carbs": 48,
  "fat": 3,
  "servingSize": "100g"
}
```

---

### 3. Recipe Extraction 🎥

**Access:** Recipes tab → "Extract" button (bottom right of Import Recipe button)

**What You See:**
- Header: "Extract Recipe"
- URL input field
- "Extract Recipe" button
- Progress messages
- Recipe card when complete

**To Test:**
1. Copy a TikTok/Instagram/YouTube link
2. Paste into URL field
   - Example: `https://www.tiktok.com/video/1234567890`
3. Tap "Extract Recipe"
4. Watch progress: "Starting extraction..." → "Processing..." → "Extraction complete!"
5. See recipe card with:
   - Title + difficulty badge
   - Cook time + servings
   - Nutrition (calories, protein, carbs, fat)
   - Ingredients list
   - Cooking steps
6. Can bookmark (heart button)

**Backend Requirement:**
```
POST /ai/extract-recipe
{
  "url": "https://www.tiktok.com/video/..."
}

Response (Initial):
{
  "id": 42,
  "taskId": "abc123",
  "status": "processing"
}

GET /ai/extract-recipe/abc123/status

Response (Completed):
{
  "id": 42,
  "title": "Thai Green Curry",
  "description": "Delicious Thai curry",
  "ingredients": [
    {"name": "Chicken", "quantity": 500, "unit": "g"},
    {"name": "Coconut milk", "quantity": 400, "unit": "ml"}
  ],
  "steps": [
    {"step": 1, "instruction": "Cut chicken..."},
    {"step": 2, "instruction": "Heat oil..."}
  ],
  "cookTimeMinutes": 25,
  "prepTimeMinutes": 10,
  "difficulty": "medium",
  "servings": 4,
  "macros": {
    "calories": 450,
    "protein": 35,
    "carbs": 30,
    "fat": 20
  },
  "status": "completed"
}
```

---

## API Configuration

### Current Setup (in Config.swift)

```swift
static let baseURL = URL(string: "http://localhost:8000")!
static let apiPrefix = "/api/v1"
```

### For Production

Update in `Kalo/Config.swift`:

```swift
// Development
static let baseURL = URL(string: "http://localhost:8000")!

// Staging
static let baseURL = URL(string: "https://staging-api.kaloapp.com")!

// Production
static let baseURL = URL(string: "https://api.kaloapp.com")!
```

---

## Debugging

### View Network Calls

1. Open Xcode Console
2. Network calls appear as:
   ```
   [NetworkingService] POST /api/v1/ai/chat
   [NetworkingService] Response: {"reply": "..."}
   ```

### Check State

**AI Chat Messages:**
```swift
// Add debug print in AIChatView
print("Messages: \(viewModel.messages)")
print("Loading: \(viewModel.isLoading)")
```

**Barcode Scanner:**
```swift
// Add debug print in BarcodeScannerViewController
print("Detected barcode: \(barcode)")
```

**Recipe Extraction:**
```swift
// Add debug print in RecipeExtractionViewModel
print("Extraction status: \(extractedRecipe?.status ?? "nil")")
```

### Simulator Issues

**Camera Not Working:**
- Barcode scanner only works on physical device
- To test in simulator, temporarily mock the response:

```swift
// In BarcodeScannerViewModel.fetchNutritionData()
let mockResponse = NutritionBarcodeResponse(
    barcode: "5901234123457",
    productName: "Mock Product",
    calories: 250,
    ...
)
return mockResponse
```

**Network Not Connecting:**
- Ensure backend is running: `docker-compose up -d api`
- Check baseURL in Config.swift
- Verify firewall/VPN allows localhost access
- Use `http://` not `https://` for localhost

---

## File Locations Reference

| Feature | Main Files |
|---------|-----------|
| AI Chat | `Views/AI/AIChatView.swift` + `ViewModels/AIChatViewModel.swift` |
| Barcode | `Views/Components/BarcodeScannerView.swift` + `ViewModels/BarcodeScannerViewModel.swift` |
| Recipe Extraction | `Views/Recipes/RecipeExtractionView.swift` + `ViewModels/RecipeExtractionViewModel.swift` |
| Tab Navigation | `Views/TabRootView.swift` |
| Models | `Models/AIMessage.swift`, `Models/Barcode.swift`, `Models/RecipeExtraction.swift` |

---

## Common Issues & Solutions

### Issue: "Type 'AIChatView' cannot find 'KaloTheme' in scope"

**Solution:** Add to AIChatView.swift top:
```swift
import SwiftUI

struct KaloTheme {
    static let mint = Color(red: 0.29, green: 0.89, blue: 0.76)
    static let divider = Color(red: 0.93, green: 0.93, blue: 0.93)
}
```

**OR** Import from Config.swift (already available in existing code)

### Issue: "BarcodeScannerView shows blank camera"

**Solution (Simulator):**
- Barcode scanning doesn't work in simulator
- Test on physical device OR mock the response
- See "Simulator Issues" section above

### Issue: "Recipe doesn't populate after extraction"

**Solution:**
- Check backend is returning recipe data
- Verify task polling is working (check console logs)
- Ensure recipe extraction endpoint returns correct JSON structure

### Issue: "AI messages don't appear"

**Solution:**
- Verify backend /ai/chat endpoint is running
- Check network tab in browser dev tools
- Enable verbose logging:

```swift
// Add to AIChatViewModel.sendMessage()
print("Sending: \(text)")
print("Response: \(response.reply)")
```

---

## Performance Tips

### Reduce Initial Load Time

**AI Chat:**
- Messages load on-demand as they're received
- Typing indicator appears immediately

**Barcode Scanner:**
- Camera view renders quickly
- Pre-compile Vision framework on first launch

**Recipe Extraction:**
- Progress indicators show extraction is running
- Polling checks status every 2 seconds
- Timeout is 30 minutes for long videos

### Optimize Network Calls

**Currently:**
- All calls use existing NetworkingService
- JSON encoding/decoding is built-in
- Token injection is automatic

**Caching (Future):**
```swift
// Could add Redis caching on backend
// or UserDefaults on iOS for offline support
```

---

## Production Checklist

Before deploying to App Store:

- [ ] Update baseURL to production API
- [ ] Test all features with production backend
- [ ] Enable HTTPS (change http:// to https://)
- [ ] Test camera permissions on real device
- [ ] Test barcode scanning with real products
- [ ] Test recipe extraction with real videos
- [ ] Verify error messages don't leak sensitive info
- [ ] Add privacy policy for camera/photo access
- [ ] Update app version in Config.swift
- [ ] Run app through TestFlight
- [ ] Get feedback on UX

---

## Next Steps

1. **Build & Run:** `Cmd+R` in Xcode
2. **Test Each Feature:** Follow testing guide above
3. **Connect Backend:** Point to your backend API
4. **Debug Issues:** Use console logs and debugging tips
5. **Deploy:** When ready for production

---

## Support

**Questions?** Check:
1. FEATURE_IMPLEMENTATION_SUMMARY.md (overview)
2. Source code comments in each file
3. Backend documentation in `/kalo-backend/`
4. Xcode console for network logs

**Need to modify?** Key files:
- Tab navigation: `Views/TabRootView.swift`
- Colors/theme: `Config.swift`
- API endpoints: `Services/NetworkingService.swift`
- Each feature's ViewModel for business logic

---

**Ready to test!** 🎉

Run the app and test all 4 new features. Each one is fully integrated and ready to connect to the backend.
