@echo off
title Movie Recommendation - Backend Server
echo ========================================
echo   Starting Backend Server (Flask)
echo ========================================
echo.

cd /d d:\final-system\backend

echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('localhost', 27017).admin.command('ping'); print('MongoDB OK')" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] MongoDB is not running!
    echo Starting MongoDB with Docker...
    docker-compose up -d
    timeout /t 3 >nul
)

echo.
echo Starting Flask server on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python run.py
