#!/bin/bash

# Concurrent Server Status Check
# Shows which servers are running and their status

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        💰 Financial Tools - Concurrent Status 💰          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Django on port 8000
echo -n "🌐 Django Server (Port 8000):     "
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ RUNNING"
    PID=$(lsof -t -i :8000 | head -1)
    echo "   └─ PID: $PID"
    echo "   └─ URL: http://localhost:8000"
else
    echo "❌ STOPPED"
fi

echo ""

# Check Ollama on port 11434
echo -n "🤖 Ollama Server (Port 11434):   "
if lsof -i :11434 >/dev/null 2>&1; then
    echo "✅ RUNNING"
    PID=$(lsof -t -i :11434 | head -1)
    echo "   └─ PID: $PID"
    echo "   └─ URL: http://localhost:11434"
    
    # Check available models
    MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*' | cut -d'"' -f4 | head -3)
    if [ ! -z "$MODELS" ]; then
        echo "   └─ Models:"
        echo "$MODELS" | while read model; do
            echo "      • $model"
        done
    fi
else
    echo "❌ STOPPED"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    CONCURRENT STATUS                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if both are running
DJANGO_RUNNING=$(lsof -i :8000 >/dev/null 2>&1 && echo true || echo false)
OLLAMA_RUNNING=$(lsof -i :11434 >/dev/null 2>&1 && echo true || echo false)

if [ "$DJANGO_RUNNING" = true ] && [ "$OLLAMA_RUNNING" = true ]; then
    echo "✅ CONCURRENT MODE: BOTH SERVERS ACTIVE"
    echo ""
    echo "📊 Quick Actions:"
    echo "   • Open Dashboard:      http://localhost:8000"
    echo "   • AI Chatbot:          http://localhost:8000/chatbot/"
    echo "   • Budget Calculator:   http://localhost:8000/budget/"
    echo "   • Financial Calc:      http://localhost:8000/calculator/"
    echo "   • Ollama API:          http://localhost:11434/api"
else
    echo "⚠️  PARTIAL MODE:"
    if [ "$DJANGO_RUNNING" = true ]; then
        echo "   ✅ Django is running"
    else
        echo "   ❌ Django is stopped"
    fi
    
    if [ "$OLLAMA_RUNNING" = true ]; then
        echo "   ✅ Ollama is running"
    else
        echo "   ❌ Ollama is stopped"
    fi
fi

echo ""
