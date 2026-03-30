@echo off
setlocal
echo ==========================================
echo    Florence-Insight Environment Setup
echo ==========================================

:: Creating virtual environment
if not exist venv_ai (
    echo Creating virtual environment (Python 3.10) - venv_ai...
    py -3.10 -m venv venv_ai
)

:: Activating environment
echo Activating venv_ai...
call venv_ai\Scripts\activate

:: Installing dependencies
echo Installing dependencies from requirements.txt...
echo This includes PyTorch with CUDA 12.1 support.
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==========================================
echo    Setup Complete!
echo    Use run_app.bat to start the server.
echo ==========================================
pause
