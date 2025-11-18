# Pull and Build Commands for RunPod

## Quick Commands

### 1. Pull Latest Code
```bash
cd /workspace/metroa-demo
git pull metroa main
```

### 2. Install/Update Dependencies
```bash
cd /workspace/metroa-demo
pip install --break-system-packages -r requirements.txt
```

### 3. Restart Backend

#### Option A: Kill and Restart (Recommended)
```bash
# Kill existing backend
pkill -f "uvicorn main:app"

# Start backend in background
cd /workspace/metroa-demo
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
```

#### Option B: Using Screen (Better for monitoring)
```bash
# Kill existing backend
pkill -f "uvicorn main:app"

# Start in screen session
cd /workspace/metroa-demo
screen -dmS metroa-backend bash -c "python -m uvicorn main:app --host 0.0.0.0 --port 8888"

# To attach to screen: screen -r metroa-backend
# To detach: Ctrl+A then D
```

#### Option C: One-liner (Quick restart)
```bash
cd /workspace/metroa-demo && pkill -f "uvicorn main:app" && nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
```

### 4. Verify Backend is Running
```bash
# Check if backend is running
curl http://localhost:8888/health

# Check logs
tail -f /workspace/metroa-demo/backend.log

# Or if using screen
screen -r metroa-backend
```

## Complete Workflow

```bash
# 1. Navigate to project
cd /workspace/metroa-demo

# 2. Pull latest code
git pull metroa main

# 3. Update dependencies (if requirements.txt changed)
pip install --break-system-packages -r requirements.txt

# 4. Kill existing backend
pkill -f "uvicorn main:app"

# 5. Start backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &

# 6. Verify
sleep 2
curl http://localhost:8888/health
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8888
lsof -i :8888

# Kill it
kill -9 <PID>
```

### Backend Not Starting
```bash
# Check logs
tail -50 /workspace/metroa-demo/backend.log

# Check Python version
python --version

# Check dependencies
pip list | grep -E "fastapi|uvicorn|opencv"
```

### Git Pull Fails
```bash
# Reset to remote (careful - loses local changes)
git fetch metroa
git reset --hard metroa/main

# Or stash local changes
git stash
git pull metroa main
git stash pop
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `git pull metroa main` | Pull latest code |
| `pip install --break-system-packages -r requirements.txt` | Update dependencies |
| `pkill -f "uvicorn main:app"` | Kill backend |
| `nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &` | Start backend |
| `curl http://localhost:8888/health` | Check backend health |
| `tail -f backend.log` | View logs |

