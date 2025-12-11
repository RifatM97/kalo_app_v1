#!/bin/bash

# Quick Start - AI Extraction Pipeline
# Fixed version that uses OpenAI Vision with actual video frames

echo "=================================================="
echo "KALO AI EXTRACTION - QUICK START"
echo "=================================================="
echo ""

# Check if backend is running
echo "Checking backend status..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend not running. Starting it now..."
    echo ""
    cd /Users/rifathossain/Desktop/kalo/kalo-backend
    
    # Kill any existing process on port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
    
    # Start backend
    PYTHONPATH=/Users/rifathossain/Desktop/kalo/kalo-backend \
      /Users/rifathossain/Desktop/kalo/.venv/bin/python -m uvicorn main:app \
      --reload --host 0.0.0.0 --port 8000 > /tmp/kalo-backend.log 2>&1 &
    
    echo "Waiting for backend to start..."
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend started successfully"
    else
        echo "❌ Failed to start backend. Check logs:"
        echo "   tail -f /tmp/kalo-backend.log"
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "BACKEND STATUS"
echo "=================================================="
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo "=================================================="
echo "WHAT WAS FIXED"
echo "=================================================="
echo ""
echo "Before: Video extraction returned 'cake with dining table'"
echo "  - Backend was NOT using OpenAI Vision"
echo "  - Only sending text to text-only model"
echo "  - Model hallucinated from fragmented text"
echo ""
echo "After: Video extraction uses Vision API with real frames"
echo "  - Backend sends 8 video frames to GPT-4o Vision"
echo "  - Model can actually SEE the cooking process"
echo "  - Returns accurate recipe data"
echo ""

echo "=================================================="
echo "HOW TO TEST"
echo "=================================================="
echo ""
echo "Option 1: Test from Terminal"
echo "  cd /Users/rifathossain/Desktop/kalo"
echo "  /Users/rifathossain/Desktop/kalo/.venv/bin/python test_extraction_fix.py"
echo ""
echo "Option 2: Test from iOS App"
echo "  1. Open Xcode:"
echo "     open /Users/rifathossain/Desktop/kalo/kalo/kalo.xcodeproj"
echo "  2. Build and Run (⌘ + R)"
echo "  3. Navigate to Recipe Extraction"
echo "  4. Paste TikTok URL:"
echo "     https://www.tiktok.com/@nourishment.nutrition/video/7580846176082087198"
echo "  5. Tap 'Extract Recipe'"
echo "  6. Wait 30-90 seconds"
echo "  7. See REAL recipe (not garbage)!"
echo ""

echo "=================================================="
echo "COST"
echo "=================================================="
echo ""
echo "Per video extraction: \$0.02-\$0.05"
echo "Your \$5 credit: ~100-250 video extractions"
echo "Worth it for accurate results!"
echo ""

echo "=================================================="
echo "BACKEND LOGS"
echo "=================================================="
echo ""
echo "View logs: tail -f /tmp/kalo-backend.log"
echo ""
echo "Look for:"
echo "  - 'Selected X frames from Y total' (frame selection)"
echo "  - 'Calling OpenAI Vision API with N frames' (Vision call)"
echo "  - '✓ Recipe structured: [dish name]' (success)"
echo ""

echo "=================================================="
echo "✅ READY TO TEST!"
echo "=================================================="
echo ""
echo "Backend is running at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Read full report: AI_EXTRACTION_FIX_REPORT.md"
echo ""
