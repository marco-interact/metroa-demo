# Test Backend Endpoints

## Backend is Running! ✅

Your backend is running (PID: 191896) and listening on port 8888.

## Test Health Endpoint

```bash
# Basic health check
curl http://localhost:8888/health

# With verbose output to see what's happening
curl -v http://localhost:8888/health

# With timeout
curl --max-time 5 http://localhost:8888/health

# Test status endpoint
curl http://localhost:8888/api/status
```

## Check Backend Logs

```bash
# If started with screen
screen -r metroa-backend

# If started with nohup
tail -f /workspace/metroa-demo/backend.log

# Check process details
ps aux | grep 191896
```

## Common Issues

### curl returns nothing
- Backend might be starting up (wait 10-30 seconds)
- Backend might be stuck in initialization
- Check logs to see what's happening

### Connection refused
- Backend crashed after starting
- Check logs for errors

### Timeout
- Backend is hanging on startup
- Check database initialization
- Check dependencies

## Force Restart

```bash
# Kill existing backend
kill 191896

# Wait a moment
sleep 2

# Start fresh
cd /workspace/metroa-demo
python main.py
```

