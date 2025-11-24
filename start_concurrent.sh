#!/bin/bash

# Concurrent Server Runner - Django + Ollama
# This script runs both Django and Ollama servers simultaneously

set -e

PROJECT_DIR="/Users/shazibsiddique/Desktop/ai capstone project "
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     💰 Financial Tools - Concurrent Server Runner 💰      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source .venv/bin/activate

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}⏹️  Shutting down servers...${NC}"
    kill $OLLAMA_PID $DJANGO_PID 2>/dev/null
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. Install from https://ollama.ai${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🚀 Starting Ollama server...${NC}"
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo -e "${GREEN}✅ Ollama started (PID: $OLLAMA_PID)${NC}"

# Give Ollama time to start
sleep 3

# Check if Ollama is responding
echo -e "${YELLOW}⏳ Waiting for Ollama to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Ollama took too long to start, continuing anyway...${NC}"
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}🚀 Starting Django server...${NC}"
python manage.py migrate > /tmp/django_migrate.log 2>&1
python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
DJANGO_PID=$!
echo -e "${GREEN}✅ Django started (PID: $DJANGO_PID)${NC}"

# Give Django time to start
sleep 2

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  🎉 SERVERS RUNNING 🎉                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📍 Services Available:${NC}"
echo -e "   🤖 Ollama:  http://localhost:11434"
echo -e "   💻 Django:  http://localhost:8000"
echo ""
echo -e "${GREEN}📊 Open in Browser:${NC}"
echo -e "   ${YELLOW}http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}📋 Log Files:${NC}"
echo -e "   /tmp/ollama.log"
echo -e "   /tmp/django.log"
echo ""
echo -e "${YELLOW}⌨️  Press Ctrl+C to stop both servers${NC}"
echo ""

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $OLLAMA_PID 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Ollama crashed, restarting...${NC}"
        ollama serve > /tmp/ollama.log 2>&1 &
        OLLAMA_PID=$!
    fi
    
    if ! kill -0 $DJANGO_PID 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Django crashed, restarting...${NC}"
        python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
        DJANGO_PID=$!
    fi
    
    sleep 5
done
