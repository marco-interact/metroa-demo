# Run Backend Persistently (Survives Terminal Disconnect)

## Problem

When you close the RunPod terminal, processes started in that terminal are killed. The backend needs to run in a way that persists.

## Solution: Use Screen (Recommended)

### Install Screen (if not installed)

```bash
apt-get update && apt-get install -y screen
```

### Start Backend in Screen

```bash
cd /workspace/metroa-demo

# Kill any existing backend
lsof -ti :8888 | xargs kill -9 2>/dev/null || true
sleep 2

# Start in screen session
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py"

# Wait and test
sleep 3
curl http://localhost:8888/health
```

### Reconnect to Screen Session

```bash
# List all screen sessions
screen -ls

# Reconnect to backend session
screen -r metroa-backend

# To detach (keep running): Press Ctrl+A then D
```

## Alternative: Use Nohup

```bash
cd /workspace/metroa-demo

# Kill existing backend
lsof -ti :8888 | xargs kill -9 2>/dev/null || true
sleep 2

# Start with nohup
nohup python main.py > backend.log 2>&1 &

# View logs
tail -f backend.log
```

## Use the Persistent Script

```bash
cd /workspace/metroa-demo
bash START_BACKEND_PERSISTENT.sh
```

This script will:
1. Kill any existing backend
2. Pull latest code
3. Start backend in screen (or nohup if screen unavailable)
4. Test the backend

## Quick One-Liner

```bash
cd /workspace/metroa-demo && lsof -ti :8888 | xargs kill -9 2>/dev/null; sleep 2 && screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py" && sleep 3 && curl http://localhost:8888/health
```

## Verify Backend is Running

```bash
# Check process
ps aux | grep "python.*main.py" | grep -v grep

# Test endpoint
curl http://localhost:8888/health

# Check screen sessions
screen -ls
```

## Stop Backend

```bash
# If using screen
screen -S metroa-backend -X quit

# Or kill by PID
lsof -ti :8888 | xargs kill -9

# Or kill by process name
pkill -9 -f "python.*main.py"
```

