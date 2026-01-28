@echo off
echo ========================================
echo  SLV Housing Market - Launcher
echo ========================================
echo.
echo Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo.
echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo Opening application in browser...
start http://localhost:5173

echo.
echo ========================================
echo  App is now running!
echo ========================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo.
echo  Minimize this window.
echo  Close it when you're done using the app.
echo ========================================
pause
