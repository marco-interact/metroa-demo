# Fix Uvicorn --reload Issues

## Problem

The backend is running with `--reload` flag which can cause:
- Memory issues
- Hanging requests
- Slow responses
- File watching overhead

## Solution: Restart Without --reload

### Step 1: Kill Current Backend

```bash
kill 191896
# Wait a moment
sleep 2
```

### Step 2: Start Without --reload

```bash
cd /workspace/metroa-demo

# Option A: Simple start
python main.py

# Option B: With screen
screen -S metroa-backend -d -m python main.py

# Option C: With nohup
nohup python main.py > backend.log 2>&1 &
```

### Step 3: Verify

```bash
sleep 3
curl http://localhost:8888/health
curl http://localhost:8888/api/status
```

## Why --reload is Problematic

- **Memory**: File watcher consumes memory
- **Performance**: Slower startup and response times
- **Stability**: Can cause hanging requests
- **Production**: Not recommended for production use

## Check Current Backend Status

```bash
# Test if it's responding
curl -v --max-time 5 http://localhost:8888/health

# Check process memory
ps aux | grep 191896 | awk '{print $6/1024 " MB"}'

# Check if it's stuck
strace -p 191896 -c -e trace=network
```

## Quick Restart Command

```bash
kill 191896 && sleep 2 && cd /workspace/metroa-demo && screen -S metroa-backend -d -m python main.py && sleep 3 && curl http://localhost:8888/health
```

