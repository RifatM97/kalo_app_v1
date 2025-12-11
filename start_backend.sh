#!/bin/bash
#
# KALO BACKEND STARTUP SCRIPT
# Production-grade startup with health checks
#

set -e

echo "🚀 Starting KALO Backend..."

# Configuration
BACKEND_DIR="/Users/rifathossain/Desktop/kalo/kalo-backend"
VENV_PYTHON="/Users/rifathossain/Desktop/kalo/.venv/bin/python"
LOG_FILE="/tmp/kalo-backend.log"
PORT=8000

# Kill any existing backend process
echo "📍 Checking for existing processes on port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null && echo "✓ Killed existing process" || echo "✓ Port $PORT is free"

# Wait for port to be released
sleep 2

# Navigate to backend directory
cd "$BACKEND_DIR"

# Start backend
echo "🔧 Starting uvicorn..."
PYTHONPATH="$BACKEND_DIR" \
"$VENV_PYTHON" -m uvicorn main:app \
  --reload \
  --host 0.0.0.0 \
  --port $PORT \
  > "$LOG_FILE" 2>&1 &

BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"

# Wait for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Health check
echo "🏥 Performing health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health)

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Backend is HEALTHY!"
    echo ""
    echo "📊 Backend Information:"
    echo "   URL: http://localhost:$PORT"
    echo "   PID: $BACKEND_PID"
    echo "   Logs: $LOG_FILE"
    echo "   API Docs: http://localhost:$PORT/docs"
    echo ""
    echo "🎯 Ready to receive requests from iOS app!"
    echo ""
    echo "📝 View logs: tail -f $LOG_FILE"
    echo "🛑 Stop backend: kill $BACKEND_PID"
else
    echo "❌ Health check failed!"
    echo "Response: $HEALTH_RESPONSE"
    echo ""
    echo "Check logs: tail -50 $LOG_FILE"
    exit 1
fi
