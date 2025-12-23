#!/bin/bash

# Recipe Analyzer V3 - Streamlit App Launcher
# This script runs the Streamlit application

echo "🍳 Starting Recipe Analyzer V3..."
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your GEMINI_API_KEY"
    echo ""
    echo "Example:"
    echo "GEMINI_API_KEY=your_api_key_here"
    echo ""
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "Installing Streamlit..."
    pip install streamlit>=1.28.0
fi

echo "✅ All checks passed!"
echo "🚀 Launching Streamlit app..."
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Streamlit app from the script directory
cd "$SCRIPT_DIR"
streamlit run app.py
