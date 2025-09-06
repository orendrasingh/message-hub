#!/bin/bash

# Production startup script for Message Hub

echo "Starting Message Hub in Production Mode..."

# Set production environment
export FLASK_ENV=production
export FLASK_APP=run.py

# Create logs directory
mkdir -p logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating template..."
    cp .env.example .env
    echo "Please edit .env file with your actual configuration before starting!"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Run database migrations
echo "Running database migrations..."
python migrate.py

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --timeout 120 \
         --keep-alive 2 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         run:app
