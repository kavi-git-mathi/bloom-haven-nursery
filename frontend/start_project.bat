@echo off
echo Starting Bloom Haven Nursery...

echo Starting Backend Server (Port 5000)...
cd backend
start cmd /k "python app.py"

timeout /t 3

echo Starting Frontend Server (Port 3000)...
cd ..\frontend
start cmd /k "python -m http.server 3000"

timeout /t 2

echo.
echo ✅ Servers started successfully!
echo 🌐 Frontend: http://127.0.0.1:3000
echo 🔧 Backend:  http://127.0.0.1:5000
echo.
echo 🚫 Ports avoided: 8000(Splunk), 8080(Jenkins), 9000(SonarQube)
echo.
echo Press any key to open the website...
pause >nul
start http://127.0.0.1:3000