# Debug Backend Crash

## Check Backend Logs

```bash
# Check if backend is running
ps aux | grep "python.*main.py" | grep -v grep

# Check recent logs
tail -50 /workspace/metroa-demo/backend.log

# Check for Python errors
tail -100 /workspace/metroa-demo/backend.log | grep -i error

# Check startup errors
tail -100 /workspace/metroa-demo/backend.log | grep -i "traceback\|exception\|failed"
```

## Common Crash Causes

### 1. Import Error
```bash
cd /workspace/metroa-demo
python3 -c "from database import db; print('Import OK')"
```

### 2. Database Lock/Corruption
```bash
cd /workspace/metroa-demo
python3 << 'PYTHON'
import sqlite3
try:
    conn = sqlite3.connect('/workspace/database.db')
    conn.execute('SELECT COUNT(*) FROM projects').fetchone()
    print("Database OK")
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
PYTHON
```

### 3. Syntax Error in Code
```bash
cd /workspace/metroa-demo
python3 -m py_compile database.py
python3 -m py_compile main.py
```

## Quick Fix: Restart with Error Output

```bash
cd /workspace/metroa-demo
pkill -f "python.*main.py" || true
sleep 2
python main.py 2>&1 | tee backend_debug.log
```

## If Cleanup Function is the Issue

Temporarily disable cleanup on startup:

```bash
cd /workspace/metroa-demo
# Edit main.py to comment out cleanup call in startup_event
sed -i 's/cleanup_duplicate_demos()/# cleanup_duplicate_demos()/g' main.py

# Or manually edit startup_event to skip cleanup
```

## Check Recent Changes

```bash
cd /workspace/metroa-demo
git log --oneline -5
git diff HEAD~1 database.py | head -50
```
