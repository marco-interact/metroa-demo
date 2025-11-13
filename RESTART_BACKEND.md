# ✅ Restart Backend with Fix Applied

**The fix is already in the code - just need to restart backend**

---

## Step 1: Kill Existing Backend

```bash
cd /workspace/metroa-demo

# Kill everything on port 8888
lsof -ti:8888 | xargs kill -9 2>/dev/null || true

# Kill any backend processes
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

# Wait
sleep 2

# Remove PID file
rm -f backend.pid
```

---

## Step 2: Start Backend

```bash
cd /workspace/metroa-demo

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3

# Start backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload \
> backend.log 2>&1 &

# Save PID
echo $! > backend.pid

# Wait for startup
sleep 5
```

---

## Step 3: Verify Backend Started

```bash
# Test health endpoint
curl http://localhost:8888/health

# Should return: {"status":"healthy",...}

# Check logs
tail -20 backend.log

# Check process
ps aux | grep uvicorn | grep -v grep
```

---

## One-Liner: Complete Restart

**Copy/paste this entire command:**

```bash
cd /workspace/metroa-demo && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && pkill -f "uvicorn.*main:app" 2>/dev/null || true && pkill -f "python.*main.py" 2>/dev/null || true && sleep 2 && rm -f backend.pid && source venv/bin/activate && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

---

## Expected Result

After running, you should see:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

If you see this, backend is running successfully! ✅

