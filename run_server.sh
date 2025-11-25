#!/bin/bash

# Start Django Financial Tools Server

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Run migrations
echo "Running migrations..."
python3 manage.py migrate

# Start the server
echo "🚀 Starting Django server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
python3 manage.py runserver 0.0.0.0:8000
