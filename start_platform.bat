@echo off
title OmniPulse E-Commerce Intelligence Platform
echo ======================================================================
echo    OMNIPULSE - E-COMMERCE INTELLIGENCE & DECISION SUPPORT PLATFORM
echo ======================================================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment Python...
    venv\Scripts\python.exe run_platform.py
) else (
    echo [INFO] Virtual environment not found, falling back to system Python...
    python run_platform.py
)

pause
