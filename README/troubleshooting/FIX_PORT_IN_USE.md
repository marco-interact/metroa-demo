# Fix Port 8888 Already In Use

## Problem

Port 8888 is already in use by another process (likely the old backend).

## Solution: Kill Process and Restart

### Step 1: Find Process Using Port 8888

```bash
lsof -i :8888
# OR
netstat -tulpn | grep 8888
# OR
ss -tulpn | grep 8888
```

### Step 2: Kill the Process

```bash
# Option A: Kill by PID (replace PID with actual process ID)
kill -9 <PID>

# Option B: Kill all Python processes (be careful!)
pkill -9 python

# Option C: Kill by port directly
fuser -k 8888/tcp
```

### Step 3: Verify Port is Free

```bash
lsof -i :8888
# Should return nothing if port is free
```

### Step 4: Start Backend

```bash
cd /workspace/metroa-demo
python main.py
```

## One-Liner Solution

```bash
# Kill process on port 8888 and start backend
fuser -k 8888/tcp 2>/dev/null; sleep 2 && cd /workspace/metroa-demo && python main.py
```

## Alternative: Use Different Port

If you can't kill the process, start on a different port:

```bash
cd /workspace/metroa-demo
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

## Find and Kill Specific Backend Process

```bash
# Find Python processes
ps aux | grep "python.*main.py"

# Kill specific process (replace PID)
kill -9 <PID>

# Or kill all uvicorn processes
pkill -9 uvicorn
```

## Complete Restart Script

```bash
#!/bin/bash
cd /workspace/metroa-demo

# Kill any process on port 8888
echo "Killing processes on port 8888..."
fuser -k 8888/tcp 2>/dev/null || pkill -9 -f "python.*main.py" || true

# Wait a moment
sleep 2

# Verify port is free
if lsof -i :8888 > /dev/null 2>&1; then
    echo "⚠️  Port 8888 still in use, trying harder..."
    killall -9 python 2>/dev/null || true
    sleep 2
fi

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Start backend
echo "Starting backend..."
python main.py
```

