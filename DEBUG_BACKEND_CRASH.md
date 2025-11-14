# Debug Backend Crash

## Step 1: Run Backend in Foreground to See Errors

```bash
cd /workspace/metroa-demo
python main.py
```

This will show the exact error. Look for:
- Import errors
- Database errors
- Syntax errors
- Missing dependencies

## Step 2: Check Python Syntax

```bash
cd /workspace/metroa-demo
python3 -m py_compile main.py
python3 -m py_compile colmap_binary_parser.py
python3 -m py_compile database.py
python3 -m py_compile pointcloud_postprocess.py
python3 -m py_compile openmvs_processor.py
```

## Step 3: Test Imports

```bash
cd /workspace/metroa-demo
python3 -c "import fastapi; print('FastAPI OK')"
python3 -c "import uvicorn; print('Uvicorn OK')"
python3 -c "from database import Database; print('Database OK')"
python3 -c "from colmap_binary_parser import MeasurementSystem; print('MeasurementSystem OK')"
python3 -c "import open3d as o3d; print('Open3D OK')"
python3 -c "import cv2; print('OpenCV OK')"
```

## Step 4: Check Database

```bash
# Check if database file exists
ls -lh /workspace/database.db

# Check permissions
chmod 644 /workspace/database.db 2>/dev/null

# Try to access database
python3 -c "import sqlite3; conn = sqlite3.connect('/workspace/database.db'); print('DB OK'); conn.close()"
```

## Step 5: Check Dependencies

```bash
cd /workspace/metroa-demo
pip install --break-system-packages -r requirements.txt
```

## Step 6: Check for Recent Code Changes

```bash
cd /workspace/metroa-demo
git pull origin main
git log --oneline -5
```

## Step 7: Check System Resources

```bash
# Check memory
free -h

# Check disk space
df -h /workspace

# Check Python version
python3 --version
```

## Step 8: Run with Python Debug Mode

```bash
cd /workspace/metroa-demo
python3 -u main.py 2>&1 | tee backend_debug.log
```

## Common Crash Causes

### 1. Import Errors
- Missing dependencies
- Syntax errors in imported modules
- Circular imports

### 2. Database Errors
- Database file locked
- Corrupted database
- Missing tables

### 3. Missing Files
- COLMAP binaries not found
- Missing configuration files
- Missing directories

### 4. Memory Issues
- Out of memory (OOM)
- Check with: `dmesg | grep -i "killed process"`

### 5. Port Conflicts
- Port 8888 already in use
- Check with: `lsof -i :8888`

## Get Full Error Traceback

```bash
cd /workspace/metroa-demo
python3 main.py 2>&1 | tee crash.log
# Then check crash.log for full error
```

## Quick Diagnostic Script

```bash
cd /workspace/metroa-demo
cat > check_backend.sh << 'EOF'
#!/bin/bash
echo "=== Python Version ==="
python3 --version

echo "=== Checking Syntax ==="
python3 -m py_compile main.py && echo "✓ main.py OK" || echo "✗ main.py ERROR"

echo "=== Checking Imports ==="
python3 -c "import fastapi" && echo "✓ FastAPI OK" || echo "✗ FastAPI ERROR"
python3 -c "import uvicorn" && echo "✓ Uvicorn OK" || echo "✗ Uvicorn ERROR"
python3 -c "from database import Database" && echo "✓ Database OK" || echo "✗ Database ERROR"

echo "=== Checking Database ==="
ls -lh /workspace/database.db && echo "✓ Database file exists" || echo "✗ Database file missing"

echo "=== Checking Dependencies ==="
pip list | grep -E "fastapi|uvicorn|open3d|opencv" || echo "✗ Dependencies missing"

echo "=== Testing Startup ==="
timeout 10 python3 main.py 2>&1 | head -20
EOF
chmod +x check_backend.sh
bash check_backend.sh
```
