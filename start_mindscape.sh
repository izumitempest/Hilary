#!/bin/bash

# Hilary AI - MindScape Startup Script
# This script starts both the FastAPI backend and the Expo frontend.

# Get the absolute path of the project directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo " Starting MindScape Development Suite..."

# 1. Start the Backend
# We start from PROJECT_ROOT and use 'python -m backend.main' to resolve imports correctly
echo " Starting Backend on http://192.168.1.164:8000..."
cd "$PROJECT_ROOT"
source "$PROJECT_ROOT/venv/bin/activate"
export PYTHONPATH="$PROJECT_ROOT"
# Run backend in background and log to backend.log
python -m backend.main > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!

# 2. Start the Frontend
echo " Starting Frontend Expo Server..."
cd "$PROJECT_ROOT/frontend"

# Function to stop both processes on Ctrl+C
cleanup() {
    echo -e "\n🛑 Shutting down MindScape..."
    kill $BACKEND_PID
    exit
}

trap cleanup SIGINT SIGTERM

echo " Backend is running (PID: $BACKEND_PID)."
echo " Logs: tail -f backend.log"
echo " Starting Expo... (Scan the QR code below)"

# Run Vite Dev Server for Web App
npm run dev