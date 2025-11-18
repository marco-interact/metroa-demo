# Quick Backend Start Commands for RunPod

## Option 1: Install Screen (Recommended)

```bash
apt-get update && apt-get install -y screen
screen -S metroa-backend -d -m python main.py
screen -r metroa-backend  # Attach to view logs
# Detach: Press Ctrl+A then D
```

## Option 2: Use nohup (No Installation Required)

```bash
cd /workspace/metroa-demo
nohup python main.py > backend.log 2>&1 &
tail -f backend.log  # View logs
# Stop: kill <PID> (find PID with: ps aux | grep "python.*main.py")
```

## Option 3: Simple Background Process

```bash
cd /workspace/metroa-demo
python main.py &
# Logs will appear in terminal
# Stop: kill %1 or find PID and kill it
```

## Option 4: Use the Start Script

```bash
cd /workspace/metroa-demo
git pull origin main
bash START_BACKEND.sh
```

## Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8888/health

# Check if process is running
ps aux | grep "python.*main.py" | grep -v grep

# Check port
lsof -i :8888
```

## Stop Backend

```bash
# Find and kill process
pkill -f "python.*main.py"

# Or if using screen
screen -S metroa-backend -X quit

# Or if using nohup (find PID first)
ps aux | grep "python.*main.py" | grep -v grep
kill <PID>
```

## One-Liner (Quick Start)

```bash
cd /workspace/metroa-demo && git pull origin main && nohup python main.py > backend.log 2>&1 & sleep 3 && curl http://localhost:8888/health
```

