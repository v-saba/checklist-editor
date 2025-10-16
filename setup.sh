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
sudo apt-get install -y texlive-xetex texlive-fonts-recommended texlive-fonts-extra fonts-paratype

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install flask flask-wtf flask-sqlalchemy gunicorn

# Create necessary directories if they don't exist
echo "Creating necessary directories..."
mkdir -p tmp
mkdir -p logs

# Create WSGI entry point if it doesn't exist
if [ ! -f wsgi.py ]; then
    echo "Creating WSGI entry point..."
    cat > wsgi.py << 'EOF'
from app import app

if __name__ == "__main__":
    app.run()
EOF
fi

# Set correct permissions
echo "Setting permissions..."
chmod +x run.sh

echo "Setup completed successfully!"
echo "You can now run the application using: ./run.sh"
