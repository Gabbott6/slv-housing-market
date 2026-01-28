@echo off
echo ========================================
echo Restarting Backend Server (Clean Start)
echo ========================================

echo.
echo Killing any running uvicorn processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul

echo.
echo Clearing Python cache...
cd /d "%~dp0"
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo Starting fresh server...
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
