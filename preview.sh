#!/bin/bash

# Simple HTTP server for previewing the blog locally
# Serves the website on http://localhost:8000

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting local server on http://localhost:$PORT"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo "Error: Python not found. Please install Python to use the preview server."
    exit 1
fi
