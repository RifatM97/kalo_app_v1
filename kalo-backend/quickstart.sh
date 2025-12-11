#!/bin/bash

# 🚀 KALO AI PIPELINE - QUICK START GUIDE

echo "════════════════════════════════════════════════════════════════"
echo "   KALO AI RECIPE EXTRACTION - QUICK START"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5] Checking Python environment...${NC}"
if [ -f "/Users/rifathossain/Desktop/kalo/.venv/bin/python" ]; then
    echo -e "${GREEN}✓ Virtual environment found${NC}"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi

# Check .env
echo ""
echo -e "${BLUE}[2/5] Checking .env configuration...${NC}"
if [ -f "/Users/rifathossain/Desktop/kalo/kalo-backend/.env" ]; then
    if grep -q "OPENAI_API_KEY" /Users/rifathossain/Desktop/kalo/kalo-backend/.env; then
        echo -e "${GREEN}✓ .env file configured with OPENAI_API_KEY${NC}"
    else
        echo -e "${RED}✗ OPENAI_API_KEY not in .env${NC}"
        echo "  Add: OPENAI_API_KEY=sk-proj-YOUR_KEY"
        exit 1
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

# Check Redis
echo ""
echo -e "${BLUE}[3/5] Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis not running. Start it:${NC}"
        echo "  redis-server"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Redis not installed (optional)${NC}"
    echo "  Install: brew install redis"
fi

# Check dependencies
echo ""
echo -e "${BLUE}[4/5] Checking Python dependencies...${NC}"
cd /Users/rifathossain/Desktop/kalo/kalo-backend

MISSING_PACKAGES=0
for package in openai yt_dlp cv2 ultralytics paddleocr flask; do
    if /Users/rifathossain/Desktop/kalo/.venv/bin/python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓ $package installed${NC}"
    else
        echo -e "${YELLOW}⚠ $package not found${NC}"
        MISSING_PACKAGES=1
    fi
done

if [ $MISSING_PACKAGES -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Installing missing packages...${NC}"
    /Users/rifathossain/Desktop/kalo/.venv/bin/pip install -r requirements.txt -q
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}[5/5] System ready!${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Start options
echo -e "${BLUE}Quick Start Options:${NC}"
echo ""
echo "1. RUN DEBUG PIPELINE TEST:"
echo "   /Users/rifathossain/Desktop/kalo/.venv/bin/python debug_pipeline.py \\\"https://www.youtube.com/shorts/dQw4w9WgXcQ\\\""
echo ""
echo "2. RUN REAL PIPELINE TEST:"
echo "   /Users/rifathossain/Desktop/kalo/.venv/bin/python test_pipeline_real.py"
echo ""
echo "3. START BACKEND SERVER:"
echo "   cd /Users/rifathossain/Desktop/kalo/kalo-backend"
echo "   /Users/rifathossain/Desktop/kalo/.venv/bin/python -m uvicorn main:app --reload"
echo ""
echo "4. START CELERY WORKER:"
echo "   cd /Users/rifathossain/Desktop/kalo/kalo-backend"
echo "   /Users/rifathossain/Desktop/kalo/.venv/bin/celery -A app.celery_app worker -l info"
echo ""
echo "5. USE DOCKER COMPOSE:"
echo "   export OPENAI_API_KEY=\\\"sk-proj-YOUR_KEY\\\""
echo "   docker-compose up"
echo ""
echo -e "${YELLOW}Note: Requires valid OpenAI API key with sufficient quota${NC}"
echo ""
