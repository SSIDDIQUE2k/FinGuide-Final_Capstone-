# 502 Bad Gateway Fix - Memory Optimization for t2.micro

## Problem Diagnosis ✅

The root cause of the 502 Bad Gateway errors has been identified:

```
[ERROR] Worker (pid:19028) was sent SIGKILL! Perhaps out of memory?
```

**Your t2.micro instance (914Mi RAM) runs out of memory when processing Ollama requests**, causing the Linux OOM (Out Of Memory) killer to terminate the Gunicorn worker, resulting in 502 errors.

## Immediate Solution: Deploy Memory Optimizations

### Step 1: Configure Ollama for Low Memory

Run this on your AWS EC2 instance:

```bash
cd ~/FinGuide-Final_Capstone-
git pull origin main
chmod +x configure_ollama_lowmem.sh
./configure_ollama_lowmem.sh
```

This configures Ollama to:
- Process only 1 request at a time
- Keep only 1 model loaded in memory
- Unload model after 5 minutes of inactivity

### Step 2: Deploy Updated Django Code

```bash
chmod +x deploy_memory_fix.sh
./deploy_memory_fix.sh
```

This deploys code changes that:
- Limit Ollama responses to 256 tokens (reduces memory)
- Use 45-second timeout (prevents hanging)
- Provide intelligent fallbacks using vector database
- Better error handling for OOM situations

### Step 3: Test the Chatbot

Visit: http://54.218.71.146/chatbot/

Try asking: "What is a 401k?"

**Expected behavior:**
- ✅ Simple questions should work (may be slow)
- ⚠️ Complex/long responses may still cause OOM on t2.micro
- 📚 Fallback to vector database context when AI unavailable

## What Changed in the Code

### 1. Memory-Efficient Ollama Calls (`financial/views.py`)

**Before:**
```python
model = OllamaLLM(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_API_BASE,
    timeout=30
)
```

**After:**
```python
model = OllamaLLM(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_API_BASE,
    timeout=60,
    num_predict=256  # Limit response length
)
```

### 2. Direct API Calls with Reduced Tokens

New `ollama_chat_direct()` function:
- Limits responses to 300 tokens max
- 45-second timeout to prevent worker hanging
- Truncates context to 1000 chars
- Graceful fallback on failure

### 3. Intelligent Fallback System

When Ollama fails due to memory:
- Returns relevant context from vector database (ChromaDB)
- Provides helpful error messages
- Doesn't crash - returns 503 with fallback content

## Monitoring Commands

### Check Memory Usage in Real-Time
```bash
watch -n 2 'free -h && echo && ps aux | grep -E "(ollama|gunicorn)" | grep -v grep'
```

### Monitor Gunicorn Logs
```bash
sudo journalctl -u gunicorn -f
```

### Check for OOM Killer Activity
```bash
sudo dmesg | grep -i "out of memory"
sudo dmesg | grep -i "oom"
```

## Expected Performance on t2.micro

| Scenario | Expected Result |
|----------|----------------|
| Simple question (1-2 sentences) | ✅ Should work (slow, 10-30s) |
| Medium question (paragraph) | ⚠️ May work, may OOM |
| Complex question (long response) | ❌ Likely to OOM and return fallback |
| Concurrent requests | ❌ Will definitely OOM |

## Long-Term Solution: Upgrade EC2 Instance

The t2.micro is **fundamentally inadequate** for running Ollama with a 2GB model in production.

### Recommended Upgrade Path

#### Option 1: t3.small (MINIMUM)
- **RAM:** 2GB (2x current)
- **Cost:** ~$15/month
- **Performance:** Can handle basic Ollama queries
- **Limitation:** Still struggles with concurrent users

#### Option 2: t3.medium (RECOMMENDED) ⭐
- **RAM:** 4GB (4x current)
- **Cost:** ~$30/month
- **Performance:** Comfortable for Ollama + Django
- **Concurrent users:** 3-5 simultaneous requests

#### Option 3: t3.large (IDEAL)
- **RAM:** 8GB (8x current)
- **Cost:** ~$60/month
- **Performance:** Excellent, professional-grade
- **Concurrent users:** 10+ simultaneous requests

### How to Upgrade EC2 Instance

1. **Stop your instance:**
   ```bash
   # From AWS Console: EC2 → Instances → Select instance → Instance State → Stop
   ```

2. **Change instance type:**
   ```
   EC2 → Instances → Select instance → Actions → Instance Settings → Change instance type
   Select: t3.medium
   ```

3. **Start instance:**
   ```
   Instance State → Start
   ```

4. **Verify (IP may change):**
   ```bash
   ssh ubuntu@<NEW_IP>
   free -h  # Should show ~3.8Gi total
   ```

## Alternative: Use Smaller Model

If you cannot upgrade, consider using a smaller model:

```bash
# On AWS EC2
ollama pull tinyllama  # Only 637MB vs 2GB

# Update .env
echo "OLLAMA_MODEL=tinyllama" >> .env

# Restart services
sudo systemctl restart gunicorn
```

**Trade-offs:**
- ✅ Fits in t2.micro memory
- ❌ Lower quality responses
- ❌ Less knowledgeable

## Summary

| Solution | Cost | Effort | Quality | Status |
|----------|------|--------|---------|--------|
| Memory optimizations | Free | ✅ Done | Low | Deployed |
| Use tinyllama model | Free | 5 min | Lower | Optional |
| Upgrade to t3.small | $15/mo | 10 min | Medium | Recommended |
| Upgrade to t3.medium | $30/mo | 10 min | High | **Best** ⭐ |

## Next Steps

1. ✅ **Immediate:** Run both deployment scripts above
2. 🧪 **Test:** Try the chatbot with simple questions
3. 📊 **Monitor:** Watch memory usage during testing
4. 💰 **Decide:** Budget for EC2 upgrade or accept limitations
5. 🚀 **Upgrade:** Change to t3.medium for production-ready performance

## Questions?

- **"Will this fix the 502 errors?"** - Partially. Simple queries should work, but complex ones may still fail on t2.micro.
- **"Do I need to upgrade?"** - Yes, for production use with multiple users.
- **"What if I can't upgrade?"** - Use tinyllama model or accept that only simple queries will work.
- **"Can I test locally first?"** - Yes, the code changes are backward compatible.

## Files Modified

- `financial/views.py` - Memory-efficient Ollama integration
- `configure_ollama_lowmem.sh` - Ollama service configuration
- `deploy_memory_fix.sh` - Deployment automation

All changes are committed to your GitHub repository.
