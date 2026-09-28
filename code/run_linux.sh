#!/bin/bash

echo "=========================================="
echo "ComicCraft - AI Comic Story Creator"
echo "=========================================="

echo ""

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo ""

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo ""
echo "Starting ComicCraft..."
echo ""

uvicorn app.main:app --reload