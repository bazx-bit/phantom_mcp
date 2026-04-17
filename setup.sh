#!/bin/bash
# Site-Ghost Setup Script (macOS / Linux)
# Run this once after cloning the repository.

set -e

echo "=========================================="
echo "   Site-Ghost Setup"
echo "=========================================="
echo ""

echo "[1/3] Installing Python dependencies..."
pip install mcp playwright Pillow nest-asyncio

echo ""
echo "[2/3] Installing Chromium browser for Playwright..."
playwright install chromium

echo ""
echo "[3/3] Creating output directories..."
mkdir -p .ghost/screenshots .ghost/video_feeds

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="
echo ""
echo "To connect to your AI:"
echo "  gemini mcp add site-ghost -- python \"$(pwd)/engine/src/server.py\""
echo ""
echo "To run tests:"
echo "  python test/engine_test.py"
echo ""
