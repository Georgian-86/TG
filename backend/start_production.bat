@echo off
REM Production startup script for TeachGenie Backend (Windows)
REM Optimized for performance with multiple workers

echo.
echo Starting TeachGenie Backend (Production Mode)
echo ================================================
echo.

REM Configuration
set HOST=0.0.0.0
set PORT=8000
set WORKERS=8
set TIMEOUT=120

echo Configuration:
echo   Host: %HOST%
echo   Port: %PORT%
echo   Workers: %WORKERS% (2x default for better concurrency)
echo   Timeout: %TIMEOUT%s
echo.

REM Activate virtual environment
call .venv\Scripts\activate

REM Start Uvicorn with optimized settings
uvicorn app.main:app ^
    --host %HOST% ^
    --port %PORT% ^
    --workers %WORKERS% ^
    --timeout-keep-alive %TIMEOUT% ^
    --log-level info ^
    --access-log
