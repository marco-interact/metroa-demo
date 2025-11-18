# 🔍 Diagnose Backend Crash on RunPod

## Problem
Backend crashes immediately after starting - port 8888 never opens.

```bash
curl http://localhost:8888/health
# curl: (7) Failed to connect to localhost port 8888
```

---

## 🚨 Step 1: Check the Actual Error

### Run Python Directly (See Real Error)

```bash
cd /workspace/metroa-demo
python main.py
```

**This will show you the actual error!** Look for:
- `ModuleNotFoundError` - Missing Python dependency
- `ImportError` - Module import failed
- `FileNotFoundError` - Missing file or database
- `PermissionError` - Permission issues
- COLMAP not found errors

---

## 🔧 Common Fixes

### Fix 1: Missing Python Dependencies

```bash
cd /workspace/metroa-demo
pip install -r requirements.txt

# If that fails, install individually:
pip install fastapi==0.115.4
pip install uvicorn[standard]==0.32.0
pip install python-multipart==0.0.12
pip install aiosqlite==0.20.0
pip install opencv-python==4.10.0.84
pip install numpy==1.26.4
pip install open3d==0.19.0
pip install python-dotenv==1.0.1
pip install pydantic==2.9.2
pip install pydantic-settings==2.6.0
```

### Fix 2: Missing COLMAP

```bash
# Check if COLMAP is installed
which colmap

# If not found, install COLMAP
apt-get update && apt-get install -y colmap

# Or use the build script:
cd /workspace/metroa-demo
bash README/scripts/build-colmap-gpu-fixed.sh
```

### Fix 3: Database Issues

```bash
# Create data directories
cd /workspace/metroa-demo
mkdir -p data/uploads data/results data/cache

# Create database
python -c "
import sqlite3
from pathlib import Path
db_path = Path('data/database.db')
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(db_path)
conn.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        name TEXT,
        video_path TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT,
        result_data TEXT
    )
''')
conn.commit()
conn.close()
print('✅ Database created')
"
```

### Fix 4: Missing System Dependencies

```bash
# Install all system dependencies
apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Verify ffmpeg
ffmpeg -version

# Verify OpenGL
glxinfo | grep "OpenGL version"
```

### Fix 5: Port Already in Use

```bash
# Check what's using port 8888
lsof -i:8888
netstat -tulpn | grep 8888

# Kill everything on port 8888
lsof -ti:8888 | xargs kill -9

# Kill Jupyter if running
jupyter notebook stop 8888
pkill -f jupyter

# Try again
python main.py
```

---

## 🐛 Step 2: Test Each Module Import

Create a test script to find which import is failing:

```bash
cd /workspace/metroa-demo

cat > test_imports.py << 'EOF'
#!/usr/bin/env python3
"""Test each import to find the failing one"""
import sys

def test_import(module_name, import_statement):
    try:
        exec(import_statement)
        print(f"✅ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False

print("Testing imports...")
test_import("FastAPI", "from fastapi import FastAPI")
test_import("Uvicorn", "import uvicorn")
test_import("OpenCV", "import cv2")
test_import("NumPy", "import numpy")
test_import("Open3D", "import open3d")
test_import("SQLite3", "import sqlite3")
test_import("Pydantic", "from pydantic import BaseModel")
test_import("AsyncIO", "import asyncio")
test_import("COLMAP Processor", "from colmap_processor import COLMAPProcessor")
test_import("COLMAP Parser", "from colmap_binary_parser import COLMAPBinaryParser")
test_import("Quality Presets", "from quality_presets import get_preset")
test_import("Pointcloud Process", "from pointcloud_postprocess import postprocess_pointcloud")
test_import("OpenMVS", "from openmvs_processor import OpenMVSProcessor")

print("\nTesting system commands...")
import subprocess
for cmd in ["colmap", "ffmpeg"]:
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=2)
        print(f"✅ {cmd} found")
    except FileNotFoundError:
        print(f"❌ {cmd} not found")
    except Exception as e:
        print(f"⚠️  {cmd}: {e}")
EOF

python test_imports.py
```

---

## 🔍 Step 3: Check Screen Session Logs

If running in screen, check what happened:

```bash
# List screen sessions
screen -ls

# Try to reattach to see output
screen -r metroa-backend

# If session is dead, check if there's a log file
ls -la /workspace/metroa-demo/*.log

# Check system logs
dmesg | tail -50
journalctl -n 50
```

---

## 📊 Step 4: Resource Check

Maybe the pod ran out of resources:

```bash
# Check memory
free -h

# Check disk space
df -h

# Check if CUDA is available
nvidia-smi

# Check running processes
ps aux | grep python
```

---

## 🚀 Step 5: Fresh Start

If nothing works, start completely fresh:

```bash
# 1. Kill everything
pkill -f python
pkill -f uvicorn
lsof -ti:8888 | xargs kill -9

# 2. Clean Python cache
cd /workspace/metroa-demo
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 3. Reinstall dependencies
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# 4. Verify COLMAP
colmap --version

# 5. Create directories
mkdir -p data/{uploads,results,cache}

# 6. Test Python directly
python main.py
# Watch for errors, then Ctrl+C

# 7. If no errors, start in screen
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py 2>&1 | tee backend.log"

# 8. Check logs
sleep 5
cat backend.log
curl http://localhost:8888/health
```

---

## 📝 Common Error Messages

### "ModuleNotFoundError: No module named 'fastapi'"
**Fix:** `pip install -r requirements.txt`

### "colmap: command not found"
**Fix:** Install COLMAP:
```bash
apt-get update && apt-get install -y colmap
# Or build from source using build script
```

### "OSError: libGL.so.1: cannot open shared object file"
**Fix:** Install OpenGL libraries:
```bash
apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### "Address already in use" or port 8888 error
**Fix:** Kill the existing process:
```bash
lsof -ti:8888 | xargs kill -9
```

### "sqlite3.OperationalError: unable to open database file"
**Fix:** Create data directory and database:
```bash
mkdir -p data
python -c "import sqlite3; sqlite3.connect('data/database.db').close()"
```

### Backend starts but crashes after a few seconds
**Fix:** Check logs for OOM (Out of Memory):
```bash
dmesg | grep -i "out of memory"
# If OOM, reduce quality settings or upgrade pod
```

---

## 🎯 Quick Diagnostic One-Liner

```bash
cd /workspace/metroa-demo && echo "=== Testing Backend Startup ===" && python -c "import sys; print(f'Python: {sys.version}'); import fastapi; print(f'FastAPI: {fastapi.__version__}'); from colmap_processor import COLMAPProcessor; print('✅ All imports OK')" && echo "=== Starting Backend ===" && timeout 10 python main.py || echo "❌ Backend failed"
```

---

## ✅ Success Indicators

When backend starts correctly, you should see:

```bash
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888
```

And health check should work:
```bash
curl http://localhost:8888/health
# {"status":"healthy","message":"Server is running","gpu_available":true}
```

---

## 🆘 Still Not Working?

Run this comprehensive diagnostic:

```bash
cd /workspace/metroa-demo

cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== System Info ==="
uname -a
python --version
pip --version

echo -e "\n=== COLMAP ==="
which colmap || echo "❌ COLMAP not found"
colmap --version || echo "❌ COLMAP not working"

echo -e "\n=== FFmpeg ==="
which ffmpeg || echo "❌ FFmpeg not found"
ffmpeg -version | head -1 || echo "❌ FFmpeg not working"

echo -e "\n=== GPU ==="
nvidia-smi || echo "❌ No GPU"

echo -e "\n=== Python Packages ==="
pip list | grep -E "(fastapi|uvicorn|opencv|numpy|open3d)"

echo -e "\n=== Port 8888 ==="
lsof -i:8888 || echo "✅ Port 8888 is free"

echo -e "\n=== Disk Space ==="
df -h /workspace

echo -e "\n=== Memory ==="
free -h

echo -e "\n=== Running Python Test ==="
python main.py &
PID=$!
sleep 5
kill $PID 2>/dev/null
curl http://localhost:8888/health || echo "❌ Backend not responding"
EOF

chmod +x diagnose.sh
./diagnose.sh
```

---

**Next Steps:**
1. Run `python main.py` directly to see the error
2. Share the error message for specific help
3. Follow the appropriate fix above
4. Test with `curl http://localhost:8888/health`


