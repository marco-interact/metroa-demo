# Kill Process on Port 8888

## Find What's Using Port 8888

```bash
# Method 1: Using lsof
lsof -i :8888

# Method 2: Using netstat
netstat -tulpn | grep 8888

# Method 3: Using ss
ss -tulpn | grep 8888

# Method 4: Using fuser
fuser 8888/tcp
```

## Kill the Process

```bash
# Option 1: Kill by PID (from lsof output)
lsof -i :8888 | awk 'NR==2 {print $2}' | xargs kill -9

# Option 2: Kill all Python processes
pkill -9 python

# Option 3: Kill all uvicorn processes
pkill -9 uvicorn

# Option 4: Force kill by port
fuser -k 8888/tcp

# Option 5: Nuclear option - kill all Python
killall -9 python
```

## Complete Kill and Restart

```bash
# Kill everything on port 8888
lsof -ti :8888 | xargs kill -9 2>/dev/null
fuser -k 8888/tcp 2>/dev/null
pkill -9 -f "python.*main.py" 2>/dev/null
pkill -9 uvicorn 2>/dev/null

# Wait
sleep 3

# Verify port is free
lsof -i :8888 || echo "Port 8888 is free"

# Start backend
cd /workspace/metroa-demo
python main.py
```

## One-Liner Kill and Restart

```bash
lsof -ti :8888 | xargs kill -9 2>/dev/null; fuser -k 8888/tcp 2>/dev/null; pkill -9 -f "python.*main.py" 2>/dev/null; sleep 3 && cd /workspace/metroa-demo && python main.py
```

