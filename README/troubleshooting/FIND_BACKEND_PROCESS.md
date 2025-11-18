# Find Backend Process on RunPod

## Problem
Backend is responding but process not showing in `ps aux | grep uvicorn`

## Solution

### Find Process Using Port 8888
```bash
# Method 1: Using lsof
lsof -i :8888

# Method 2: Using netstat
netstat -tlnp | grep 8888

# Method 3: Using ss
ss -tlnp | grep 8888

# Method 4: Using fuser
fuser 8888/tcp
```

### Find All Python Processes
```bash
# Find all Python processes
ps aux | grep python

# Find processes with uvicorn in command
ps aux | grep -E "uvicorn|python.*main"
```

### Kill Process Using Port 8888
```bash
# Get PID from lsof
PID=$(lsof -t -i:8888)
kill -9 $PID

# Or manually
kill -9 <PID>
```

### Restart Backend Properly
```bash
cd /workspace/metroa-demo

# Kill any existing process
pkill -f "uvicorn main:app"
pkill -f "python.*main:app"

# Wait a moment
sleep 2

# Verify port is free
lsof -i :8888

# Start backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &

# Verify it started
sleep 2
curl http://localhost:8888/health
```

## Quick Fix

```bash
cd /workspace/metroa-demo
pkill -9 -f "python.*main"
sleep 2
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
sleep 2
curl http://localhost:8888/health
```

