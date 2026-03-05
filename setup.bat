@echo off
echo ==========================================
echo    Arise Voice Assistant - Setup Script
echo ==========================================
echo.

# Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b
)

echo [1/2] Updating pip...
python -m pip install --upgrade pip

echo [2/2] Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [TIP] If PyAudio installation failed, trying via pipwin...
    pip install pipwin
    pipwin install pyaudio
    echo [2/2] Retrying standard dependencies...
    pip install -r requirements.txt
)

echo.
echo ==========================================
echo    Setup Complete!
echo    You can now run the assistant using:
echo    python modular_assistant/main.py
echo ==========================================
echo.
pause
