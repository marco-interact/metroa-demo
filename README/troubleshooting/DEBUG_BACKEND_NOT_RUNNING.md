# Debug Backend Not Running

## Step 1: Check if Backend Process is Running

```bash
# Check for Python processes
ps aux | grep "python.*main.py" | grep -v grep

# Check if port 8888 is in use
lsof -i :8888 || netstat -tuln | grep 8888

# Check process status
pgrep -af "python.*main.py"
```

## Step 2: Check Backend Logs

```bash
cd /workspace/metroa-demo

# Check recent logs
tail -50 backend.log

# Check for errors
tail -100 backend.log | grep -i "error\|traceback\|exception\|failed"

# Check startup messages
tail -100 backend.log | grep -i "startup\|ready\|uvicorn\|application"
```

## Step 3: Try Starting Backend Manually (See Errors)

```bash
cd /workspace/metroa-demo

# Kill any existing process
pkill -f "python.*main.py" || true
sleep 2

# Start in foreground to see errors
python main.py
```

## Step 4: Verify Dependencies Installed

```bash
# Check FastAPI
python3 -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"

# Check Uvicorn
python3 -c "import uvicorn; print('Uvicorn OK')"

# Check all critical imports
python3 << 'PYTHON'
try:
    import fastapi
    import uvicorn
    import sqlite3
    import cv2
    import numpy
    import open3d
    print("✅ All dependencies OK")
except ImportError as e:
    print(f"❌ Missing: {e}")
PYTHON
```

## Step 5: Check Database File

```bash
cd /workspace/metroa-demo

# Check if database exists
ls -lh /workspace/database.db

# Test database connection
python3 << 'PYTHON'
import sqlite3
try:
    conn = sqlite3.connect('/workspace/database.db')
    conn.execute('SELECT COUNT(*) FROM projects').fetchone()
    print("✅ Database OK")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
PYTHON
```

## Step 6: Check Python Version

```bash
# Check Python version
python3 --version
python --version

# Make sure we're using the right Python
which python3
which python
```

## Step 7: Try Starting with Explicit Python Path

```bash
cd /workspace/metroa-demo

# Kill existing
pkill -f "python.*main.py" || true
sleep 2

# Start with explicit python3
nohup python3 main.py > backend.log 2>&1 &

# Or try with uvicorn directly
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
```

## Step 8: Check File Permissions

```bash
cd /workspace/metroa-demo

# Check if main.py is executable
ls -l main.py

# Check if we can read the file
head -5 main.py
```

## Common Issues

### Issue 1: Import Error
If you see import errors, install missing packages:
```bash
pip install --break-system-packages <missing-package>
```

### Issue 2: Port Already in Use
```bash
# Find what's using port 8888
lsof -i :8888

# Kill it
kill -9 <PID>
```

### Issue 3: Database Locked
```bash
# Check database locks
lsof /workspace/database.db

# If locked, restart might help
```

### Issue 4: Missing Environment Variables
```bash
# Check if DATABASE_PATH is set
echo $DATABASE_PATH

# Set if needed
export DATABASE_PATH=/workspace/database.db
```
