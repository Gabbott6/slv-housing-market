@echo off
echo ========================================
echo  SLV Housing Market - Backend Restart
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] Stopping any running servers...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Clearing Python cache...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/4] Starting backend server...
echo.
echo ========================================
echo  Server will start on: http://localhost:8000
echo  Press Ctrl+C to stop
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
