#!/bin/bash

echo "========================================"
echo "AI Detection System - Starting..."
echo "========================================"
echo ""

echo "[1/2] Starting Backend API Server..."
python run_server.py &
API_PID=$!

sleep 3

echo "[2/2] Opening Frontend..."
if command -v xdg-open > /dev/null; then
    xdg-open frontend/index.html
elif command -v open > /dev/null; then
    open frontend/index.html
else
    echo "Please open frontend/index.html manually"
fi

echo ""
echo "========================================"
echo "System Started Successfully!"
echo "========================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: frontend/index.html"
echo ""
echo "Press Ctrl+C to stop the server"

wait $API_PID
