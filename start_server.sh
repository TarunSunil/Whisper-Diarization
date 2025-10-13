#!/bin/bash

echo "Starting Whisper Diarization Frontend Server..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Please run this script from the whisper-diarization root directory"
    echo "Current directory should contain backend/app.py"
    exit 1
fi

# Install Python dependencies if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to install some dependencies"
        echo "You may need to install them manually"
    fi
    echo
fi

# Create necessary directories
mkdir -p backend/uploads
mkdir -p backend/outputs

# Start the Flask server
echo "Starting Flask server on http://localhost:5000"
echo
echo "Frontend will be available at: http://localhost:5000"
echo "API endpoints available at: http://localhost:5000/api/"
echo
echo "Press Ctrl+C to stop the server"
echo

cd backend
python3 app.py