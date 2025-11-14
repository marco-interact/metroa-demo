# Pull and Build Commands for RunPod

## Quick One-Liner

```bash
cd /workspace/metroa-demo && git pull origin main && pip install --break-system-packages -r requirements.txt && pkill -f "python.*main.py" || true && sleep 2 && nohup python3 main.py > backend.log 2>&1 &
```

## Step-by-Step Commands

### Step 1: Pull Latest Code
```bash
cd /workspace/metroa-demo
git pull origin main
```

### Step 2: Install/Update Dependencies (if needed)
```bash
pip install --break-system-packages -r requirements.txt
```

### Step 3: Restart Backend
```bash
# Kill existing backend
pkill -f "python.*main.py" || true
sleep 2

# Start backend
cd /workspace/metroa-demo
nohup python3 main.py > backend.log 2>&1 &

# Wait for startup
sleep 5
```

### Step 4: Verify Backend is Running
```bash
# Check process
ps aux | grep "python.*main.py" | grep -v grep

# Check logs
tail -20 backend.log

# Test endpoint
curl http://localhost:8888/health || curl http://localhost:8888/api/status
```

## If Backend Fails to Start

### Check for Errors
```bash
tail -50 backend.log | grep -i error
```

### Common Issues

**1. Missing Dependencies**
```bash
pip install --break-system-packages fastapi uvicorn python-multipart aiosqlite opencv-python numpy open3d
```

**2. Port Already in Use**
```bash
lsof -i :8888
kill -9 <PID>
```

**3. Database Locked**
```bash
# Restart usually fixes this
pkill -f "python.*main.py"
sleep 2
python3 main.py
```

## Frontend Build (Vercel)

On your local machine:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Deploy to Vercel
vercel --prod
```

Or if using GitHub integration, Vercel will auto-deploy on push to main.
