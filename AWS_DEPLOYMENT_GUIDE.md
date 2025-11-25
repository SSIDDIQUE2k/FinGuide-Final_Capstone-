# AWS Deployment Guide - Fixing Ollama "Bad Gateway" Error

## The Problem
The chatbot shows `Error: Unexpected token 'b', "bad gateway" is not valid JSON` because Ollama is not running on your AWS EC2 instance.

## Solution: Install and Configure Ollama on AWS

### Step 1: SSH into Your AWS Instance
```bash
ssh -i your-key.pem ubuntu@54.218.71.146
```

### Step 2: Install Ollama
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### Step 3: Pull the Required Model
```bash
# Pull the llama3.2 model (or whichever model you're using)
ollama pull llama3.2:latest

# Verify the model is available
ollama list
```

### Step 4: Configure Ollama as a System Service
Create a systemd service file to ensure Ollama starts automatically:

```bash
sudo nano /etc/systemd/system/ollama.service
```

Add this content:
```ini
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
```

### Step 5: Start and Enable Ollama
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Ollama
sudo systemctl start ollama

# Enable Ollama to start on boot
sudo systemctl enable ollama

# Check status
sudo systemctl status ollama
```

### Step 6: Verify Ollama is Working
```bash
# Test the API
curl http://localhost:11434/api/tags

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:latest",
  "prompt": "Hello",
  "stream": false
}'
```

### Step 7: Update Django Settings (if needed)
Ensure your Django settings on AWS have the correct configuration:

```python
# In settings.py or .env on AWS
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### Step 8: Restart Your Django Application
```bash
# If using systemd
sudo systemctl restart your-django-app

# If using screen/tmux
# Stop the current process and restart:
python manage.py runserver 0.0.0.0:8000
```

## Verification Checklist

After completing these steps, verify:

1. ✅ Ollama service is running: `sudo systemctl status ollama`
2. ✅ Model is loaded: `ollama list`
3. ✅ API responds: `curl http://localhost:11434/api/tags`
4. ✅ Django server is running
5. ✅ Chatbot works without "bad gateway" error

## Alternative: Use a Remote Ollama Service

If you don't want to run Ollama on AWS (it requires significant resources), you can:

1. Run Ollama on a separate, more powerful server
2. Update `OLLAMA_API_BASE` to point to that server
3. Ensure network security groups allow traffic between servers

Example:
```python
OLLAMA_API_BASE=http://your-ollama-server:11434
```

## Resource Requirements

**Minimum for llama3.2:latest:**
- 4GB RAM
- 2GB disk space for model
- 2 CPU cores recommended

**Recommended AWS Instance:**
- t3.medium or larger
- t3.large for better performance

## Troubleshooting

### If Ollama Won't Start
```bash
# Check logs
sudo journalctl -u ollama -f

# Check if port is already in use
sudo netstat -tulpn | grep 11434

# Kill any conflicting process
sudo pkill ollama
sudo systemctl start ollama
```

### If Model Download Fails
```bash
# Check disk space
df -h

# Try pulling a smaller model first
ollama pull llama3.2:3b
```

### If "Bad Gateway" Persists
```bash
# Check Django logs
tail -f /path/to/django/logs

# Test Ollama directly from Django server
python manage.py shell
>>> import requests
>>> requests.get('http://localhost:11434/api/tags').json()
```

## Graceful Degradation

The updated code includes fallback behavior:
- If Ollama is unavailable, the chatbot will still provide context from the vector database
- Users see a helpful error message instead of JSON parsing errors
- The app doesn't crash when Ollama is down

## Next Steps

1. Deploy this code to AWS
2. Install and configure Ollama on AWS
3. Test the chatbot functionality
4. Monitor resource usage and scale if needed

---

**Need help?** Check the Django logs and Ollama service status first.
