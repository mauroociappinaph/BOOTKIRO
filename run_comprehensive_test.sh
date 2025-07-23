#!/bin/bash

# Comprehensive test runner for Personal Automation Bot
# This script will activate the virtual environment and run all tests

echo "🚀 Starting Personal Automation Bot Comprehensive Test Suite"
echo "============================================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found, using system Python"
fi

# Check if requirements are installed
echo "🔍 Checking dependencies..."
python -c "import telegram, google.auth, groq" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Core dependencies found"
else
    echo "📥 Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Run the comprehensive test
echo "🧪 Starting comprehensive tests..."
python comprehensive_test.py

echo "📊 Test suite completed!"
echo "Check test_report.json for detailed results"
