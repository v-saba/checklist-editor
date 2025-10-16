#!/bin/bash

# Exit on error
set -e

echo "Setting up Checklist Application..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install XeLaTeX and required fonts
echo "Installing XeLaTeX and fonts..."
sudo apt-get install -y texlive-xetex texlive-fonts-recommended texlive-fonts-extra

# Create virtual environment in parent directory
echo "Creating Python virtual environment..."
cd ..
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install flask flask-wtf gunicorn

# Create necessary directories if they don't exist
echo "Creating necessary directories..."
mkdir -p checklist_app/tmp
mkdir -p checklist_app/logs

# Create WSGI entry point if it doesn't exist
if [ ! -f checklist_app/wsgi.py ]; then
    echo "Creating WSGI entry point..."
    cat > checklist_app/wsgi.py << 'EOF'
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    app.run()
EOF
fi

# Set correct permissions
echo "Setting permissions..."
chmod +x checklist_app/run.sh

echo "Setup completed successfully!"
echo "You can now run the application using: cd checklist_app && ./run.sh" 