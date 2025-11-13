# Debug Setup Script Failure

**Check what failed:**

```bash
# Check backend logs
tail -50 /workspace/metroa-demo/backend.log

# Check if backend process is running
ps aux | grep -E "python|uvicorn" | grep -v grep

# Check if port 8888 is in use
lsof -i :8888

# Check Python environment
cd /workspace/metroa-demo && source venv/bin/activate && python3 -c "import main"
```

**Common issues and fixes:**

**Issue 1: Import errors**
```bash
cd /workspace/metroa-demo && source venv/bin/activate && pip install -r requirements.txt
```

**Issue 2: Syntax errors**
```bash
cd /workspace/metroa-demo && git pull origin main
```

**Issue 3: Port already in use**
```bash
lsof -ti:8888 | xargs kill -9 && sleep 2
```

**Issue 4: Database path error**
```bash
mkdir -p /workspace/data && export DATABASE_PATH=/workspace/data/database.db
```

**Restart backend manually:**
```bash
cd /workspace/metroa-demo && source venv/bin/activate && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 DATABASE_PATH=/workspace/data/database.db && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

