@echo off
echo Starting Whisper Diarization Frontend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo Error: Please run this script from the whisper-diarization root directory
    echo Current directory should contain backend\app.py
    pause
    exit /b 1
)

REM Install Python dependencies if requirements.txt exists
if exist "backend\requirements.txt" (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo Warning: Failed to install some dependencies
        echo You may need to install them manually
    )
    echo.
)

REM Create necessary directories
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\outputs" mkdir "backend\outputs"

REM Start the Flask server
echo Starting Flask server on http://localhost:5000
echo.
echo Frontend will be available at: http://localhost:5000
echo API endpoints available at: http://localhost:5000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python app.py