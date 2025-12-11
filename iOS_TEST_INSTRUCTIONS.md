# iOS AI Extraction - Testing Instructions

## ✅ Integration Complete!

The iOS app is now fully integrated with the AI backend. Here's how to test it **TODAY**.

---

## 🎯 What You Can Test

### ✅ Image Extraction
Upload a recipe image (from camera or photo library) → Get structured recipe with ingredients, steps, and macros

### ✅ Video URL Extraction  
Paste a TikTok, Instagram, or YouTube recipe video URL → Get extracted recipe

### ⏳ Video Upload (Future)
Direct video upload from iOS (backend ready, UI needs video picker)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Verify Backend is Running
```bash
# From Terminal, check backend status:
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","service":"kalo-api","version":"1.0.0"}
```

✅ **If running**: Proceed to Step 2  
❌ **If not running**: Run `cd /Users/rifathossain/Desktop/kalo && ./start_backend.sh`

---

### Step 2: Open iOS Project
```bash
cd /Users/rifathossain/Desktop/kalo/kalo
open kalo.xcodeproj
```

---

### Step 3: Build & Run the App
1. **Select Simulator/Device**: Choose "iPhone 15 Pro" (or any iOS 17+ device)
2. **Build**: Press `⌘ + B` (Command + B)
3. **Run**: Press `⌘ + R` (Command + R)

**Build Time**: ~30-60 seconds (first build may take longer)

---

### Step 4: Navigate to Recipe Extraction
In the running app:
1. Open the app (should show main screen)
2. Navigate to **Recipe Extraction** view
3. You'll see three options:
   - **Choose Image** button
   - **Take Photo** button  
   - **Video URL** text field

---

### Step 5: Test AI Extraction

#### Option A: Image Extraction (Recommended for First Test)
1. **Tap "Choose Image"** button
2. **Select a recipe photo** from your simulator's photo library
   - If simulator has no photos, use "Take Photo" instead
3. **Wait for extraction** (5-10 seconds)
4. **View results**:
   - Recipe title
   - Ingredients with quantities
   - Step-by-step instructions
   - Macros (calories, protein, carbs, fat)
   - Cook time, servings, difficulty

#### Option B: Video URL Extraction
1. **Copy a recipe video URL**:
   - TikTok: `https://www.tiktok.com/@username/video/123456789`
   - Instagram: `https://www.instagram.com/reel/ABC123DEF/`
   - YouTube: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. **Paste URL** into "Video URL" text field
3. **Tap "Extract Recipe"** button
4. **Wait for extraction** (20-60 seconds for video processing)
5. **View results** (same as image extraction)

---

## 📱 iOS Code Updates (Already Done)

### Files Modified:
✅ **Config.swift**
- Updated `apiPrefix` from `/api/v1` to `/api`
- Already set to `http://localhost:8000` for development

✅ **NetworkingService.swift**
- Added `uploadFile()` method for multipart form data uploads
- Supports image/video file uploads with proper headers

✅ **RecipeExtractionViewModel.swift**
- Added `extractFromImage(_ image: UIImage)` method
- Added `extractFromVideo(_ videoURL: URL)` method  
- Both call `NetworkingService.shared.uploadFile()`

✅ **RecipeExtractionView.swift**
- Added `PhotosPicker` for photo library access
- Added camera button with `ImagePicker` wrapper
- Added image preview with remove/extract buttons
- Added loading states and error handling
- Existing URL extraction unchanged

---

## 🧪 Expected Behavior

### ✅ Success Case (Image)
1. **Select image** → Image preview appears
2. **Tap "Extract Recipe"** → Loading spinner shows
3. **Wait 5-10 seconds** → "Analyzing image..." progress text
4. **Recipe appears** with:
   - ✅ Title (e.g., "Grilled Chicken Salad")
   - ✅ Ingredients list with quantities
   - ✅ Numbered steps
   - ✅ Macros (calories, protein, carbs, fat)
   - ✅ Cook time, servings, difficulty

### ✅ Success Case (URL)
1. **Paste URL** → URL appears in text field
2. **Tap "Extract Recipe"** → Loading spinner shows
3. **Wait 20-60 seconds** → "Processing video..." progress text
4. **Recipe appears** (same structure as image)

### ❌ Error Cases (Expected)
- **Invalid URL**: "Failed to extract recipe: Invalid URL format"
- **Network error**: "Failed to extract recipe: The Internet connection appears to be offline"
- **Backend down**: "Failed to extract recipe: Could not connect to the server"

---

## 🔍 Debugging

### Backend Logs
```bash
# View real-time backend logs
tail -f /tmp/kalo-backend.log

# Check recent errors
tail -n 50 /tmp/kalo-backend.log | grep ERROR
```

### iOS Console
In Xcode, open **Console** (bottom panel) to see:
- Network requests
- API responses
- Error messages

### Test Backend Directly
```bash
# Test image extraction endpoint
curl -X POST http://localhost:8000/api/recipes/extract-from-image \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/recipe_image.jpg"

# Test URL extraction endpoint
curl -X POST http://localhost:8000/api/ai/extract-recipe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/123"}'
```

---

## 💰 OpenAI Cost Tracking

### Current Status
- **Balance**: $5.00 OpenAI credits
- **Cost per extraction**: ~$0.01
- **Estimated capacity**: ~500 recipe extractions

### Models Used
- **Image extraction**: GPT-4o Vision ($0.005/image) + GPT-4o-mini for macros ($0.001)
- **Video extraction**: GPT-4o Vision (multiple frames) + Whisper transcription

### Monitor Usage
Check usage at: https://platform.openai.com/usage

---

## 📊 Backend Status Reference

### Running Process
```bash
# Check if backend is running
ps aux | grep uvicorn

# Expected output:
# rifathossain  48100  ... uvicorn main:app --host 0.0.0.0 --port 8000
```

### Restart Backend
```bash
cd /Users/rifathossain/Desktop/kalo
./start_backend.sh

# Logs will be at /tmp/kalo-backend.log
```

### Stop Backend
```bash
# Find PID
ps aux | grep uvicorn

# Kill process
kill <PID>
```

---

## 🎉 Success Criteria

After testing, you should be able to:

✅ **Upload recipe images** from iOS app  
✅ **Take photos** with camera and extract recipes  
✅ **Paste video URLs** and get extracted recipes  
✅ **View structured recipe data** (ingredients, steps, macros)  
✅ **See loading states** and error messages  
✅ **Backend processes requests** without errors

---

## 📝 Next Steps (Optional Enhancements)

### 1. Add Video Upload from iOS
Currently supports URL extraction only. To add video upload:
- Add video picker to RecipeExtractionView
- Call `viewModel.extractFromVideo(videoURL)`
- Backend already supports `/api/recipes/extract-from-video`

### 2. Save Extracted Recipes
Add functionality to:
- Save recipe to local database
- Add to meal plan
- Share with friends

### 3. Batch Extraction
Allow users to:
- Upload multiple images at once
- Extract all recipes in parallel
- View extraction queue

### 4. Recipe Editing
After extraction:
- Allow manual edits to ingredients/steps
- Adjust macros
- Add notes/tags

---

## 🆘 Common Issues

### Issue 1: "Could not connect to the server"
**Cause**: Backend not running  
**Solution**: Run `./start_backend.sh` from `/Users/rifathossain/Desktop/kalo`

### Issue 2: "Invalid image format"
**Cause**: Unsupported image type  
**Solution**: Use JPEG or PNG images only

### Issue 3: "Extraction taking too long"
**Cause**: Large video file or slow network  
**Solution**: Wait up to 60 seconds, or use smaller videos/images

### Issue 4: Build errors in Xcode
**Cause**: Missing dependencies  
**Solution**: 
```bash
cd /Users/rifathossain/Desktop/kalo/kalo
xcodebuild clean
```
Then rebuild (⌘ + B)

---

## 📚 API Documentation

### Image Extraction Endpoint
```http
POST /api/recipes/extract-from-image
Content-Type: multipart/form-data

file: <binary image data>

Response:
{
  "title": "Grilled Chicken Salad",
  "ingredients": [
    {"name": "Chicken breast", "quantity": 200, "unit": "g"},
    {"name": "Mixed greens", "quantity": 2, "unit": "cups"}
  ],
  "steps": [
    {"step": 1, "instruction": "Season chicken with salt and pepper"},
    {"step": 2, "instruction": "Grill for 6-8 minutes per side"}
  ],
  "macros": {
    "calories": 350,
    "protein": 42,
    "carbs": 12,
    "fat": 15
  },
  "cook_time_minutes": 20,
  "prep_time_minutes": 10,
  "servings": 2,
  "difficulty": "Easy"
}
```

### URL Extraction Endpoint
```http
POST /api/ai/extract-recipe
Content-Type: application/json

{
  "url": "https://www.tiktok.com/@user/video/123"
}

Response:
{
  "task_id": "abc-123-def",
  "status": "processing"
}

# Poll status:
GET /api/ai/extract-recipe/abc-123-def/status

Response (when complete):
{
  "status": "completed",
  "title": "...",
  "ingredients": [...],
  ...
}
```

---

## ✨ That's It!

You're now ready to test AI-powered recipe extraction in your iOS app!

**Questions?** Check backend logs at `/tmp/kalo-backend.log` or iOS console in Xcode.

**Ready to deploy?** See `DEPLOYMENT.md` for production setup instructions.
