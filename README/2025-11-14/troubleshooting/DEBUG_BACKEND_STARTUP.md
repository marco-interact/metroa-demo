# 🔧 Debug Backend Startup Failure

**Backend failed to start - troubleshooting steps**

---

## Step 1: Check Backend Logs

**On RunPod terminal:**

```bash
cd /workspace/metroa-demo
tail -50 backend.log
```

This will show the actual error message.

---

## Step 2: Common Issues and Fixes

### Issue 1: Port Already in Use

**Check:**
```bash
lsof -i :8888
```

**Fix:**
```bash
# Kill process on port 8888
lsof -ti:8888 | xargs kill -9

# Wait a moment
sleep 2

# Try starting again
cd /workspace/metroa-demo
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

---

### Issue 2: Missing Python Dependencies

**Check:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip list | grep -E "fastapi|uvicorn|open3d"
```

**Fix:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Issue 3: Import Errors

**Check:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "from database import db; print('OK')"
python3 -c "from colmap_processor import COLMAPProcessor; print('OK')"
python3 -c "from quality_presets import get_preset; print('OK')"
python3 -c "from pointcloud_postprocess import postprocess_pointcloud; print('OK')"
python3 -c "from openmvs_processor import OpenMVSProcessor; print('OK')"
```

**If any fail, check the error message.**

---

### Issue 4: Database Path Issues

**Check:**
```bash
ls -la /workspace/data/database.db
```

**Fix:**
```bash
mkdir -p /workspace/data
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "from database import db; db.setup_demo_data()"
```

---

## Step 3: Manual Backend Start (Debug Mode)

**Run backend in foreground to see errors:**

```bash
cd /workspace/metroa-demo
source venv/bin/activate

# Set environment variables
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
export DATABASE_PATH=/workspace/data/database.db

# Start backend (will show errors in terminal)
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

**This will show the exact error message.**

---

## Step 4: Check Python Version

**Verify Python version:**
```bash
python3 --version
# Should be Python 3.10 or higher
```

---

## Step 5: Verify All Files Exist

```bash
cd /workspace/metroa-demo
ls -la main.py
ls -la database.py
ls -la colmap_processor.py
ls -la quality_presets.py
ls -la pointcloud_postprocess.py
ls -la openmvs_processor.py
```

---

## Quick Fix: Restart Backend

**Try this first:**

```bash
cd /workspace/metroa-demo

# Kill any existing process
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
sleep 2

# Activate venv
source venv/bin/activate

# Start backend
QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 \
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload \
> backend.log 2>&1 &

echo $! > backend.pid
sleep 5

# Check if it's running
curl http://localhost:8888/health
```

---

## Most Likely Issues

1. **Port conflict** - Something else using port 8888
2. **Missing dependencies** - Open3D or other packages not installed
3. **Import error** - New modules (quality_presets, pointcloud_postprocess, openmvs_processor) not found
4. **Database path** - Database file path issue

**Check the logs first to see the actual error!**

