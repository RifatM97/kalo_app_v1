#!/bin/bash

# Test iOS Connection to Backend
# This script simulates what the iOS app will do

echo "🧪 Testing iOS → Backend Connection"
echo "===================================="
echo ""

# Test 1: Health Check
echo "📡 Test 1: Health Check"
echo "Endpoint: GET http://localhost:8000/health"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Backend is healthy"
    echo "Response: $HEALTH"
else
    echo "❌ Backend health check failed"
    exit 1
fi
echo ""

# Test 2: API Documentation
echo "📚 Test 2: API Documentation"
echo "Endpoint: GET http://localhost:8000/docs"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ API docs accessible at http://localhost:8000/docs"
else
    echo "❌ API docs not accessible"
    exit 1
fi
echo ""

# Test 3: Image Upload Endpoint (without file)
echo "🖼️  Test 3: Image Upload Endpoint"
echo "Endpoint: POST http://localhost:8000/api/recipes/extract-from-image"
UPLOAD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/recipes/extract-from-image)
if [ "$UPLOAD_STATUS" = "422" ]; then
    echo "✅ Upload endpoint exists (422 = missing file, as expected)"
elif [ "$UPLOAD_STATUS" = "401" ]; then
    echo "⚠️  Upload endpoint requires authentication (we can add token later)"
else
    echo "❌ Upload endpoint returned unexpected status: $UPLOAD_STATUS"
    exit 1
fi
echo ""

# Test 4: URL Extraction Endpoint
echo "🔗 Test 4: URL Extraction Endpoint"
echo "Endpoint: POST http://localhost:8000/api/ai/extract-recipe"
URL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/ai/extract-recipe \
    -H "Content-Type: application/json" \
    -d '{"url": "test"}')
if [ "$URL_STATUS" = "422" ] || [ "$URL_STATUS" = "400" ] || [ "$URL_STATUS" = "200" ]; then
    echo "✅ URL extraction endpoint is responding"
else
    echo "⚠️  URL extraction endpoint status: $URL_STATUS"
fi
echo ""

# Test 5: CORS Headers (iOS needs these)
echo "🌐 Test 5: CORS Headers"
echo "Checking for Access-Control-Allow-Origin header..."
CORS_HEADER=$(curl -s -I http://localhost:8000/health | grep -i "access-control")
if [ -n "$CORS_HEADER" ]; then
    echo "✅ CORS enabled:"
    echo "$CORS_HEADER"
else
    echo "⚠️  CORS headers not found (may need to add for production)"
fi
echo ""

# Summary
echo "======================================"
echo "✅ All critical tests passed!"
echo "======================================"
echo ""
echo "📱 iOS App is ready to connect to:"
echo "   http://localhost:8000"
echo ""
echo "🎯 Available endpoints:"
echo "   • GET  /health"
echo "   • GET  /docs (API documentation)"
echo "   • POST /api/recipes/extract-from-image"
echo "   • POST /api/recipes/extract-from-video"
echo "   • POST /api/ai/extract-recipe"
echo ""
echo "🚀 Next steps:"
echo "   1. Open Xcode: open /Users/rifathossain/Desktop/kalo/kalo/kalo.xcodeproj"
echo "   2. Build: ⌘ + B"
echo "   3. Run: ⌘ + R"
echo "   4. Test recipe extraction with images!"
echo ""
