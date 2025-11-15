# Restart Backend - Step by Step

## Commands (run one at a time)

```bash
# Step 1: Navigate to project
cd /workspace/metroa-demo

# Step 2: Kill existing backend
kill -9 365563

# Step 3: Wait for port to be free
sleep 2

# Step 4: Verify port is free
lsof -i :8888

# Step 5: Start backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &

# Step 6: Wait for startup
sleep 3

# Step 7: Verify it's running
curl http://localhost:8888/health

# Step 8: Check new PID
lsof -i :8888
```

## Alternative: Use semicolons instead of &&

```bash
cd /workspace/metroa-demo; kill -9 365563; sleep 2; nohup python -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 & sleep 3; curl http://localhost:8888/health; lsof -i :8888
```

