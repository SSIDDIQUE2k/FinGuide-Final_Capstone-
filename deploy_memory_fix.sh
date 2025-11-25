#!/bin/bash
# Deployment script for memory-optimized Ollama integration
# Run this on your AWS EC2 instance

set -e

echo "🚀 Deploying memory-optimized chatbot..."

# Navigate to project directory
cd ~/FinGuide-Final_Capstone-

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Restart Gunicorn
echo "🔄 Restarting Gunicorn with optimizations..."
sudo systemctl restart gunicorn

# Wait for service to start
sleep 3

# Check status
echo "✅ Checking service status..."
sudo systemctl status gunicorn --no-pager | head -10

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "💡 Key improvements:"
echo "   - Reduced Ollama response token limit (256 tokens)"
echo "   - Added 45-second timeout to prevent hanging"
echo "   - Intelligent fallback to vector database when AI unavailable"
echo "   - Better error handling for OOM situations"
echo ""
echo "🧪 Test your chatbot at: http://54.218.71.146/chatbot/"
echo ""
echo "⚠️  IMPORTANT: If 502 errors persist, your t2.micro instance"
echo "    needs to be upgraded to t3.medium (4GB RAM) for production use."
echo ""
echo "📊 Monitor memory usage:"
echo "    watch -n 2 'free -h && echo && ps aux | grep -E \"(ollama|gunicorn)\" | grep -v grep'"
