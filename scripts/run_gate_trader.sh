#!/bin/bash
# Gate.io Trading Bot - Quick Start Script

echo "🚀 Starting Gate.io Trading Bot..."
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your Gate.io API credentials"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the bot
echo ""
echo "🤖 Launching Gate.io Trading Agent..."
echo ""

python3 run_gate_trader.py

echo ""
echo "✅ Bot stopped"
