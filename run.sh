#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Set Flask environment variables
export FLASK_ENV=production
export FLASK_DEBUG=0

# Run Gunicorn
echo "Starting Checklist Application with Gunicorn..."
gunicorn --workers 3 \
         --bind unix:checklist.sock \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         --capture-output \
         wsgi:app 