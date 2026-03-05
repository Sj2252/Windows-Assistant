@echo off
setlocal

:: Get the directory where this script is located
set "APP_DIR=%~dp0"

:: Change to the application directory to ensure correct relative imports
cd /d "%APP_DIR%"

echo ==========================================
echo    Starting Arise Voice Assistant...
echo ==========================================

:: Check if python exists
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in your system path.
    echo Please run setup.bat first or install Python.
    pause
    exit /b
)

:: Run the assistant in the background
:: The 'start' command allows the shortcut to stay "decoupled" from the terminal if needed
python modular_assistant/main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The assistant failed to start.
    echo Check if dependencies are installed.
    pause
)

exit /b
