@echo off
:: Killing old instances to avoid port and VRAM conflicts
taskkill /F /IM python.exe /T >nul 2>&1

if exist venv_ai (
    echo Activating environment venv_ai...
    call venv_ai\Scripts\activate
) else if exist venv (
    echo Activating environment venv...
    call venv\Scripts\activate
) else (
    echo Virtual environment NOT FOUND. Please run install_venv.bat first!
    pause
    exit /b
)

echo Initializing Database...
python db.py

echo Checking Model Assets (Florence-2)...
python setup_model.py

echo Starting Server (Debug Mode: Auto-reload enabled)...
python app.py
pause
