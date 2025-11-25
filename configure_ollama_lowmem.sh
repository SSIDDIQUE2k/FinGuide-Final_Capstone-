#!/bin/bash
# Configure Ollama for low-memory environments (t2.micro)
# Run this on your AWS EC2 instance

echo "⚙️  Configuring Ollama for low-memory operation..."

# Stop Ollama service
sudo systemctl stop ollama

# Update Ollama service with memory limits
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=exec
ExecStart=/usr/local/bin/ollama serve
User=ubuntu
Group=ubuntu
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=5m"

[Install]
WantedBy=default.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start Ollama
sudo systemctl start ollama

# Wait for startup
sleep 5

# Verify it's running
echo ""
echo "✅ Ollama configuration updated!"
sudo systemctl status ollama --no-pager | head -10

echo ""
echo "🔧 Applied optimizations:"
echo "   - OLLAMA_NUM_PARALLEL=1 (process one request at a time)"
echo "   - OLLAMA_MAX_LOADED_MODELS=1 (keep only one model in memory)"
echo "   - OLLAMA_KEEP_ALIVE=5m (unload model after 5 min of inactivity)"
echo ""
echo "💡 This reduces memory usage but limits concurrent requests."
