# 🔧 Reset Port 8888 and Restart Backend

**Complete reset of port 8888 and backend restart**

---

## Step 1: Kill All Processes on Port 8888

**On RunPod terminal:**

```bash
# Find what's using port 8888
lsof -i :8888

# Kill all processes on port 8888
lsof -ti:8888 | xargs kill -9 2>/dev/null || true

# Double check it's free
lsof -i :8888
# Should return nothing
```

---

## Step 2: Clean Up Backend Process Files

```bash
cd /workspace/metroa-demo

# Remove PID file if exists
rm -f backend.pid

# Check for any Python processes
ps aux | grep "uvicorn\|python.*main.py" | grep -v grep

# Kill any remaining backend processes
pkill -f "uvicorn.*main:app" || true
pkill -f "python.*main.py" || true

# Wait a moment
sleep 2
```

---

## Step 3: Pull Latest Code (with fix)

```bash
cd /workspace/metroa-demo
git pull origin main
```

---

## Step 4: Restart Backend Cleanly

```bash
cd /workspace/metroa-demo

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
export DATABASE_PATH=/workspace/data/database.db

# Start backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload \
> backend.log 2>&1 &

# Save PID
echo $! > backend.pid

# Wait for startup
sleep 5

# Verify it's running
curl http://localhost:8888/health
```

---

## One-Liner: Complete Reset and Restart

**Copy/paste this entire command:**

```bash
cd /workspace/metroa-demo && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && pkill -f "uvicorn.*main:app" 2>/dev/null || true && pkill -f "python.*main.py" 2>/dev/null || true && sleep 3 && rm -f backend.pid && git pull origin main && source venv/bin/activate && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

---

## Verify Backend is Running

```bash
# Check process
ps aux | grep uvicorn | grep -v grep

# Check port
lsof -i :8888

# Test health endpoint
curl http://localhost:8888/health

# Check logs
tail -20 backend.log
```

---

## If Still Failing

**Check logs for errors:**
```bash
tail -50 backend.log
```

**Test backend manually (foreground mode to see errors):**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

This will show errors directly in the terminal.

