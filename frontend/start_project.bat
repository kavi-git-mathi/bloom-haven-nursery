@echo off
title Bloom Haven Nursery Launcher
echo ========================================
echo    Bloom Haven Nursery - Plant Store
echo ========================================
echo.

echo Checking for existing servers...
taskkill /f /im python.exe >nul 2>&1
echo Stopped any existing Python servers.
timeout /t 2

echo Starting Backend Server (Port 5000)...
cd backend
start "Backend Server" cmd /k "python app.py"

echo Waiting for backend to initialize...
timeout /t 3

echo Starting Frontend Server (Port 3000)...
cd ..\frontend
start "Frontend Server" cmd /k "python -m http.server 3000"

echo Waiting for frontend to start...
timeout /t 2

echo.
echo ✅ SERVERS STARTED SUCCESSFULLY!
echo.
echo 🌐 Frontend: http://127.0.0.1:3000
echo 🔧 Backend:  http://127.0.0.1:5000
echo.
echo To restart: Close these windows and run this file again.
echo.
echo Press any key to open the website...
pause >nul

echo Opening Bloom Haven Nursery...
start http://127.0.0.1:3000

echo.
echo 💡 TIP: If you see broken images, refresh the page (F5)
pause