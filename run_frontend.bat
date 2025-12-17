@echo off
title Movie Recommendation - Frontend Server
echo ========================================
echo   Starting Frontend Server (Next.js)
echo ========================================
echo.

cd /d d:\final-system\frontend

echo Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting Next.js dev server on http://localhost:3000
echo Press Ctrl+C to stop
echo.

npm run dev
