# 🔧 Quick RunPod Backend Restart Guide

## ⚠️ Backend Offline - Follow These Steps

### Step 1: Open Mac Terminal (NOT Docker container)

```bash
# If you're in a Docker container, exit first
exit

# Or open a new Terminal window/tab
# Cmd+T (new tab) or Cmd+N (new window)
```

---

### Step 2: SSH into RunPod from Mac Terminal

```bash
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519
```

**If you get "Permission denied" or key not found:**

```bash
# List available SSH keys
ls -la ~/.ssh/

# If you don't have id_ed25519, try other keys:
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_rsa

# Or without specifying key (will try all available keys)
ssh root@203.57.40.132 -p 10164
```

---

### Step 3: Once Connected to RunPod, Restart Backend

```bash
# Navigate to project
cd /workspace/metroa-demo

# Check if backend is running
ps aux | grep uvicorn

# If running, kill it
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    sleep 2
fi

# Alternative: Kill all Python processes on port 8888
lsof -ti:8888 | xargs kill -9 2>/dev/null || true

# Pull latest changes from GitHub
git fetch metroa
git pull metroa main

# Check for conflicts
git status

# Activate Python environment
source venv/bin/activate

# Verify GPU is available
nvidia-smi

# Start backend
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Wait for startup
sleep 5

# Check if backend is running
ps aux | grep uvicorn

# Test backend locally
curl http://localhost:8888/health

# View recent logs
tail -50 backend.log
```

**Expected Output:**
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/database.db"}
```

---

### Step 4: Test from Mac Terminal

```bash
# In a NEW terminal window/tab (keep SSH session open)
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health
```

---

## 🔍 Troubleshooting

### Issue: SSH Key Not Found

**Solution 1: Find your SSH key**
```bash
# On Mac terminal
ls -la ~/.ssh/

# Common key names:
# - id_ed25519
# - id_rsa
# - id_ecdsa
```

**Solution 2: Use password authentication**
```bash
ssh root@203.57.40.132 -p 10164
# Then enter password when prompted
```

**Solution 3: Generate new SSH key**
```bash
# On Mac terminal
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

# Add to RunPod
ssh-copy-id -i ~/.ssh/id_ed25519 root@203.57.40.132 -p 10164
```

---

### Issue: Backend Still Not Starting

**Check logs for errors:**
```bash
# On RunPod
tail -100 /workspace/metroa-demo/backend.log
```

**Common issues:**

1. **Port already in use:**
```bash
lsof -ti:8888 | xargs kill -9
```

2. **Python environment issues:**
```bash
cd /workspace/metroa-demo
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Git conflicts:**
```bash
git status
git stash  # Save local changes
git pull metroa main
git stash pop  # Restore local changes
```

4. **Database locked:**
```bash
# Stop all Python processes
pkill -9 python3
# Restart backend
cd /workspace/metroa-demo
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

---

### Issue: Can't Connect to RunPod

**Check RunPod status:**
1. Go to https://www.runpod.io/console/pods
2. Find your pod: `8pexe48luksdw3`
3. Check status (should be "Running")
4. Get SSH command from RunPod dashboard

**Alternative connection:**
```bash
# If port or IP changed, use the SSH command from RunPod dashboard
# It will look like:
ssh root@<NEW_IP> -p <NEW_PORT> -i ~/.ssh/id_ed25519
```

---

## 📊 Monitor Backend Health

### Real-time logs (on RunPod):
```bash
tail -f /workspace/metroa-demo/backend.log
```

### GPU status:
```bash
watch -n 1 nvidia-smi
```

### Check if backend is responding:
```bash
# From Mac
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/api/status
```

---

## 🎯 Quick Commands Summary

### Mac Terminal:
```bash
# Connect to RunPod
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519

# Test backend
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health
```

### On RunPod (after SSH):
```bash
# Restart backend
cd /workspace/metroa-demo
kill $(cat backend.pid) 2>/dev/null || true
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Check status
curl http://localhost:8888/health
tail -20 backend.log
```

---

## ✅ Success Indicators

1. **SSH Connected**: You see `root@<hostname>:~#` prompt
2. **Backend Running**: `ps aux | grep uvicorn` shows Python process
3. **Health Check**: `curl http://localhost:8888/health` returns JSON
4. **External Access**: `curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health` works from Mac

---

## 📞 Need Help?

**Can't SSH?**
- Get SSH command from RunPod dashboard
- Try without `-i` flag: `ssh root@203.57.40.132 -p 10164`
- Check if pod is running in RunPod console

**Backend won't start?**
- Check logs: `tail -100 backend.log`
- Check GPU: `nvidia-smi`
- Check Python: `python3 --version` (should be 3.12)

**Still stuck?**
- Restart the entire pod from RunPod dashboard
- Wait 2-3 minutes for pod to fully start
- Try SSH again

