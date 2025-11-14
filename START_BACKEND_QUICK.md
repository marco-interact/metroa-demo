# Quick Backend Start

**One-liner to start backend:**

```bash
cd /workspace/metroa-demo && source venv/bin/activate && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 DATABASE_PATH=/workspace/data/database.db && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

**Verify it's running:**

```bash
ps aux | grep uvicorn | grep -v grep
curl http://localhost:8888/health
```

**Check logs if it fails:**

```bash
tail -50 /workspace/metroa-demo/backend.log
```

