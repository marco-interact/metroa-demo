# 🔧 Fix Backend Offline - Complete Troubleshooting

**Run these commands on RunPod terminal to get backend running**

---

## ⚡ Quick Fix (Copy/Paste All)

**Run this entire block on RunPod:**

```bash
cd /workspace/metroa-demo

# 1. Pull latest code (with syntax fix)
git pull origin main

# 2. Kill everything on port 8888
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# 3. Activate venv and check Python syntax
source venv/bin/activate
python3 -m py_compile main.py && echo "✅ Syntax OK" || echo "❌ Syntax Error!"

# 4. Check imports
python3 -c "import main; print('✅ Imports OK')" || echo "❌ Import Error!"

# 5. Start backend
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# 6. Wait and test
sleep 5
curl http://localhost:8888/health && echo "" && echo "✅ BACKEND IS RUNNING!" || echo "❌ Backend failed - check logs below"
tail -30 backend.log
```

---

## 🔍 If Backend Still Fails

### Check Error Logs

```bash
cd /workspace/metroa-demo
tail -50 backend.log
```

### Check What's Running on Port 8888

```bash
lsof -i :8888
ps aux | grep -E "python|uvicorn" | grep -v grep
```

### Test Python Import Manually

```bash
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "import main"
```

If this fails, check which module is missing:

```bash
python3 -c "from quality_presets import get_preset"
python3 -c "from pointcloud_postprocess import postprocess_pointcloud"
python3 -c "from openmvs_processor import OpenMVSProcessor"
python3 -c "from database import db"
```

### Reinstall Dependencies if Needed

```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Start Backend in Foreground (See Errors Live)

**Run this to see errors in real-time:**

```bash
cd /workspace/metroa-demo
source venv/bin/activate
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

Press `Ctrl+C` to stop, then restart in background:

```bash
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

---

## ✅ Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8888/health

# Should return:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}

# Test from outside (from your Mac)
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health
```

---

## 📋 Common Issues & Fixes

### Issue: SyntaxError
**Fix:** Already fixed in latest code - just `git pull origin main`

### Issue: ModuleNotFoundError
**Fix:** `pip install -r requirements.txt`

### Issue: Port already in use
**Fix:** `lsof -ti:8888 | xargs kill -9`

### Issue: Database path error
**Fix:** `mkdir -p /workspace/data`

---

## 🎯 One-Liner: Complete Reset & Start

**Copy/paste this entire command:**

```bash
cd /workspace/metroa-demo && git pull origin main && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && pkill -f "python.*main.py" 2>/dev/null || true && pkill -f "uvicorn" 2>/dev/null || true && sleep 2 && source venv/bin/activate && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health && echo "" && echo "✅ BACKEND RUNNING!" || (echo "❌ FAILED - Check logs:" && tail -30 backend.log)
```

