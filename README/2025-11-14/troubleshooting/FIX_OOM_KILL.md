# Fix Out of Memory (OOM) Kill

**Exit 137 = Process killed due to OOM (Out of Memory)**

## Step 1: Check Logs

```bash
tail -50 /workspace/metroa-demo/backend.log
dmesg | tail -20 | grep -i "killed\|oom"
```

## Step 2: Check Memory Usage

```bash
free -h
ps aux --sort=-%mem | head -10
```

## Step 3: Start Backend Without Reload (Saves Memory)

**The `--reload` flag uses more memory. Use this instead:**

```bash
cd /workspace/metroa-demo && source venv/bin/activate && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 DATABASE_PATH=/workspace/data/database.db && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

**Note:** Removed `--reload` flag to save memory.

## Step 4: If Still Fails, Check Python Import

```bash
cd /workspace/metroa-demo && source venv/bin/activate && python3 -c "import main; print('OK')"
```

## Step 5: Alternative - Use Python Directly

```bash
cd /workspace/metroa-demo && source venv/bin/activate && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 DATABASE_PATH=/workspace/data/database.db && nohup python3 main.py > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

