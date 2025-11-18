# Start Backend Clean

## Start Backend (Foreground - See Output)

```bash
cd /workspace/metroa-demo
python main.py
```

## Start Backend (Background - Screen)

```bash
cd /workspace/metroa-demo
screen -S metroa-backend -d -m python main.py
sleep 3
curl http://localhost:8888/health
```

## Start Backend (Background - Nohup)

```bash
cd /workspace/metroa-demo
nohup python main.py > backend.log 2>&1 &
sleep 3
curl http://localhost:8888/health
tail -f backend.log
```

## Verify Backend is Running

```bash
# Check process
ps aux | grep "python.*main.py" | grep -v grep

# Test health endpoint
curl http://localhost:8888/health

# Test status endpoint
curl http://localhost:8888/api/status

# Check logs (if using nohup)
tail -f backend.log
```

## Complete Clean Start

```bash
cd /workspace/metroa-demo && python main.py
```

Press `Ctrl+C` to stop if running in foreground.

