#!/bin/bash

# Development startup script for Message Hub

echo "Starting Message Hub in Development Mode..."

# Set development environment
export FLASK_ENV=development
export FLASK_APP=run.py

# Create virtual environment if it doesn't exist
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
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating development .env file..."
    cp .env.example .env
    echo "Please edit .env file with your actual configuration!"
fi

# Start the development server
echo "Starting development server..."
python run.py
