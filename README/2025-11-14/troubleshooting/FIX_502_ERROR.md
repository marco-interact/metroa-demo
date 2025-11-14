# 🔧 Fix 502 Error - Backend Not Responding

**502 error means backend isn't accessible. Follow these steps:**

---

## 🔍 Step 1: Check if Backend is Running

**On RunPod terminal, run:**

```bash
# Check if process is running
ps aux | grep -E "python|uvicorn" | grep -v grep

# Check if port 8888 is listening
lsof -i :8888
netstat -tulpn | grep 8888

# Check backend logs
cd /workspace/metroa-demo
tail -50 backend.log
```

---

## 🚀 Step 2: Start/Restart Backend

**If backend is NOT running, start it:**

```bash
cd /workspace/metroa-demo

# Activate venv
source venv/bin/activate

# Kill any existing processes
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

# Set environment variables
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
export DATABASE_PATH=/workspace/data/database.db

# Start backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Wait and test
sleep 5
curl http://localhost:8888/health
```

---

## 🔍 Step 3: Check Backend Logs for Errors

**If backend fails to start, check logs:**

```bash
cd /workspace/metroa-demo
tail -50 backend.log
```

**Common errors:**

### Error: ModuleNotFoundError
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: SyntaxError
```bash
git pull origin main
```

### Error: Address already in use
```bash
lsof -ti:8888 | xargs kill -9
sleep 2
```

### Error: Database path issue
```bash
mkdir -p /workspace/data
export DATABASE_PATH=/workspace/data/database.db
```

---

## 🔧 Step 4: Verify Backend Configuration

**Check main.py is listening on correct host/port:**

```bash
cd /workspace/metroa-demo
grep -n "uvicorn.run\|--host\|--port" main.py || echo "Using uvicorn command"
```

**Backend MUST listen on `0.0.0.0:8888` (not `127.0.0.1` or `localhost`)**

---

## 🧪 Step 5: Test Locally on Pod

**Test backend from INSIDE the pod:**

```bash
# Test health endpoint
curl http://localhost:8888/health

# Test status endpoint
curl http://localhost:8888/api/status

# Test with 0.0.0.0
curl http://0.0.0.0:8888/health
```

**If these work but public URL doesn't, it's a RunPod proxy issue.**

---

## 🌐 Step 6: Check RunPod Port Configuration

**Verify port 8888 is exposed:**

1. Go to RunPod Dashboard
2. Check pod `8pexe48luksdw3`
3. Verify port `8888` is exposed/public
4. Check if proxy URL is correct: `https://8pexe48luksdw3-8888.proxy.runpod.net`

---

## 🔄 Step 7: Complete Restart

**Full restart sequence:**

```bash
cd /workspace/metroa-demo

# Pull latest code
git pull origin main

# Activate venv
source venv/bin/activate

# Reinstall dependencies (if needed)
pip install -r requirements.txt

# Kill everything
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 3

# Ensure data directory exists
mkdir -p /workspace/data

# Set environment
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
export DATABASE_PATH=/workspace/data/database.db

# Start backend (VERIFY: --host 0.0.0.0)
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Wait
sleep 5

# Test locally
echo "Testing locally..."
curl http://localhost:8888/health

# Check process
ps aux | grep uvicorn | grep -v grep

# Show logs
echo ""
echo "Last 20 lines of logs:"
tail -20 backend.log
```

---

## ✅ Expected Result

**After running Step 7, you should see:**

```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

**If you see this locally but still get 502 from public URL:**
- Wait 1-2 minutes for RunPod proxy to update
- Check RunPod dashboard for port configuration
- Try accessing: `https://8pexe48luksdw3-8888.proxy.runpod.net/health`

---

## 🆘 Still Getting 502?

**Run this diagnostic:**

```bash
cd /workspace/metroa-demo

echo "=== Process Check ==="
ps aux | grep -E "python|uvicorn" | grep -v grep

echo ""
echo "=== Port Check ==="
lsof -i :8888

echo ""
echo "=== Local Test ==="
curl -v http://localhost:8888/health

echo ""
echo "=== Backend Logs (last 30 lines) ==="
tail -30 backend.log

echo ""
echo "=== Environment Check ==="
echo "DATABASE_PATH: $DATABASE_PATH"
echo "Python: $(which python3)"
echo "Uvicorn: $(which uvicorn)"
```

**Share this output for further debugging.**

