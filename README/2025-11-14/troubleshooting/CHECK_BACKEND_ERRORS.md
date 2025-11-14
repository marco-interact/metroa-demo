# 🔍 Check Backend Startup Errors

**Backend failed to start - check logs for errors**

---

## Step 1: Check Backend Logs

**On RunPod terminal:**

```bash
cd /workspace/metroa-demo
tail -50 backend.log
```

This will show the actual error message.

---

## Step 2: Common Issues

### Issue 1: Import Errors (Missing Modules)

**Check:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "import main"
```

**If errors, check missing modules:**
```bash
python3 -c "from quality_presets import get_preset"
python3 -c "from pointcloud_postprocess import postprocess_pointcloud"
python3 -c "from openmvs_processor import OpenMVSProcessor"
```

**Fix missing modules:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue 2: Syntax Errors

**Check:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
python3 -m py_compile main.py
```

**If errors, check the specific file mentioned.**

---

### Issue 3: Port Already in Use

**Check:**
```bash
lsof -i :8888
netstat -tulpn | grep 8888
```

**Fix:**
```bash
lsof -ti:8888 | xargs kill -9
sleep 2
```

---

### Issue 4: Database Path Issues

**Check:**
```bash
ls -la /workspace/data/database.db
mkdir -p /workspace/data
```

---

## Step 3: Start Backend in Foreground (See Errors)

**Run backend in foreground to see errors directly:**

```bash
cd /workspace/metroa-demo
source venv/bin/activate
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

This will show errors in the terminal.

---

## Quick Debug Commands

```bash
cd /workspace/metroa-demo

# Check logs
tail -50 backend.log

# Check if process is running
ps aux | grep uvicorn

# Check port
lsof -i :8888

# Test Python import
source venv/bin/activate
python3 -c "import main; print('OK')"
```

