#!/bin/bash

# Setup script for YouTube Recipe Analyzer

echo "🍳 Setting up YouTube Recipe Analyzer..."
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✓ uv installed"
    echo ""
else
    echo "✓ uv is already installed"
    echo ""
fi

# Sync dependencies with uv (automatically creates venv and installs)
echo "Syncing dependencies with uv..."
cd .. && uv sync && cd recipe_analyzer
echo "✓ Dependencies synced"
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GEMINI_API_KEY"
    echo ""
else
    echo ".env file already exists"
    echo ""
fi

# Create outputs directory
echo "Creating outputs directory..."
mkdir -p outputs
echo "✓ outputs directory created"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ../.env and add your GEMINI_API_KEY"
echo "2. Run the app with uv: uv run python -m recipe_analyzer.app <youtube_url>"
echo ""
echo "Example:"
echo "  uv run python -m recipe_analyzer.app 'https://youtube.com/shorts/abc123' --servings 2"
echo ""
