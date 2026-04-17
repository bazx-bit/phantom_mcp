@echo off
REM Site-Ghost Setup Script (Windows)
REM Run this once after cloning the repository.

echo ==========================================
echo    Site-Ghost Setup
echo ==========================================
echo.

echo [1/3] Installing Python dependencies...
pip install mcp playwright Pillow nest-asyncio
if %ERRORLEVEL% neq 0 (
    echo FAILED: pip install failed. Ensure Python 3.10+ is installed.
    exit /b 1
)

echo.
echo [2/3] Installing Chromium browser for Playwright...
playwright install chromium
if %ERRORLEVEL% neq 0 (
    echo FAILED: Playwright browser install failed.
    exit /b 1
)

echo.
echo [3/3] Creating output directories...
mkdir .ghost\screenshots 2>nul
mkdir .ghost\video_feeds 2>nul

echo.
echo ==========================================
echo    Setup Complete!
echo ==========================================
echo.
echo To connect to Gemini CLI:
echo   gemini mcp add site-ghost -- python "%~dp0engine\src\server.py"
echo.
echo To run tests:
echo   set PYTHONIOENCODING=utf-8
echo   python test\engine_test.py
echo.
