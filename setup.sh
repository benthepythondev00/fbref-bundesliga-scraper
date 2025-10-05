#!/bin/bash

echo "=========================================="
echo "Multi-Sport Scraper - Setup"
echo "=========================================="
echo ""

if [ ! -d "venv" ]; then
    echo "✅ Creating virtual environment..."
    python3.11 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "✅ Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installing Playwright browsers..."
playwright install chromium

echo ""
echo "=========================================="
echo "Setup completed successfully! ✅"
echo "=========================================="
echo ""
echo "To run the scraper:"
echo "  source venv/bin/activate"
echo "  python main.py --stathead"
echo ""
echo "To run specific sports with premium data:"
echo "  python main.py --sports bundesliga nfl --stathead"
echo ""
echo "Without premium data:"
echo "  python main.py --sports bundesliga"
echo ""
echo "For help:"
echo "  python main.py --help"
echo ""