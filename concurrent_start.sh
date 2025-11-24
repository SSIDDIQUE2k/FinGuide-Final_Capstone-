#!/bin/bash

# Simple concurrent launcher - Start Django + Ollama together

PROJECT_DIR="/Users/shazibsiddique/Desktop/ai capstone project "
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    💰 Starting Concurrent Servers (Django + Ollama) 💰    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Activate venv
source .venv/bin/activate

# Start Ollama in background
echo "🚀 Starting Ollama..."
ollama serve &
OLLAMA_PID=$!
echo "   Ollama PID: $OLLAMA_PID"

# Wait for Ollama to initialize
sleep 3

# Start Django in background
echo "🚀 Starting Django..."
python manage.py runserver &
DJANGO_PID=$!
echo "   Django PID: $DJANGO_PID"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ BOTH SERVERS RUNNING ✅                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Access at: http://localhost:8000"
echo "🤖 Ollama:   http://localhost:11434"
echo ""
echo "📋 Process IDs:"
echo "   Django: $DJANGO_PID"
echo "   Ollama: $OLLAMA_PID"
echo ""
echo "⌨️  Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo 'Stopping servers...'; kill $OLLAMA_PID $DJANGO_PID; exit 0" SIGINT

# Wait for processes
wait
