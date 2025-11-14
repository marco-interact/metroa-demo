# Fix Scan Failure - Pull Latest Code

**The error is already fixed in the latest code. Pull and restart:**

```bash
cd /workspace/metroa-demo && git pull origin main && lsof -ti:8888 | xargs kill -9 2>/dev/null || true && source venv/bin/activate && export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 DATABASE_PATH=/workspace/data/database.db && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & echo $! > backend.pid && sleep 5 && curl http://localhost:8888/health
```

**What was fixed:**
- Removed invalid `--SiftMatching.max_error` option from feature matching
- This option doesn't exist in COLMAP

**After restart, try uploading a scan again.**

