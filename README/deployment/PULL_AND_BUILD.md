# Pull and Build Commands for RunPod

Quick reference for updating the backend on RunPod after pushing changes to GitHub.

## 🔄 Pull Latest Code

```bash
# Navigate to project directory
cd /workspace/metroa-demo

# Pull latest changes from GitHub
git pull origin main

# Or if using 'metroa' remote:
git pull metroa main

# Force update if needed (use with caution):
git fetch origin
git reset --hard origin/main
```

## 🔨 Build/Install Dependencies

### Python Dependencies

```bash
cd /workspace/metroa-demo

# Install/update Python dependencies
pip install --break-system-packages -r requirements.txt

# Or if using virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verify Dependencies

```bash
# Check key packages
python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python3 -c "import open3d as o3d; print(f'Open3D {o3d.__version__}')"
python3 -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

## 🚀 Restart Backend

### Option 1: Simple Start (Foreground)

```bash
cd /workspace/metroa-demo
python main.py
```

### Option 2: Background with nohup

```bash
cd /workspace/metroa-demo
nohup python main.py > backend.log 2>&1 &
```

### Option 3: Using screen (Recommended)

```bash
# Install screen if needed
apt-get update && apt-get install -y screen

# Start backend in screen session
cd /workspace/metroa-demo
screen -S metroa-backend -d -m python main.py

# Attach to screen session to view logs
screen -r metroa-backend

# Detach: Press Ctrl+A then D
```

### Option 4: Kill and Restart

```bash
# Find and kill existing backend process
ps aux | grep "python.*main.py" | grep -v grep
kill -9 <PID>

# Or kill all Python processes (use with caution)
pkill -f "python.*main.py"

# Restart backend
cd /workspace/metroa-demo
python main.py
```

## ✅ Verify Backend is Running

```bash
# Check if backend is responding
curl http://localhost:8888/health

# Check backend status endpoint
curl http://localhost:8888/api/status

# Check running processes
ps aux | grep "python.*main.py" | grep -v grep

# Check if port 8888 is in use
lsof -i :8888
```

## 🔍 View Logs

```bash
# If using nohup
tail -f /workspace/metroa-demo/backend.log

# If using screen
screen -r metroa-backend

# Check system logs
journalctl -u metroa-backend  # If running as service
```

## 📋 Complete Update Workflow

```bash
# 1. Pull latest code
cd /workspace/metroa-demo
git pull origin main

# 2. Install dependencies (if requirements.txt changed)
pip install --break-system-packages -r requirements.txt

# 3. Kill existing backend
pkill -f "python.*main.py"

# 4. Start backend
cd /workspace/metroa-demo
screen -S metroa-backend -d -m python main.py

# 5. Verify
sleep 3
curl http://localhost:8888/health
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check for errors
python main.py

# Check Python version
python3 --version  # Should be 3.12+

# Check database
ls -lh /workspace/database.db

# Check disk space
df -h /workspace
```

### Port already in use

```bash
# Find process using port 8888
lsof -i :8888

# Kill it
kill -9 <PID>

# Or use different port
PORT=8000 python main.py
```

### Dependencies missing

```bash
# Reinstall all dependencies
pip install --break-system-packages --force-reinstall -r requirements.txt

# Check specific package
pip show opencv-python
pip show open3d
pip show fastapi
```
