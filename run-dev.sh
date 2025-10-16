#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
#source venv/bin/activate

# Set Flask environment variables for development
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Create necessary directories if they don't exist
mkdir -p tmp
mkdir -p logs

echo "Starting Checklist Application in development mode..."
echo "Server will be available at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Flask development server with hot reload
python -m flask run --host=0.0.0.0 --port=8000 --reload

