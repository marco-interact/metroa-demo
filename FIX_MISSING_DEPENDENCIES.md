# Fix Missing Python Dependencies

## Quick Fix Commands

```bash
# 1. Navigate to project directory
cd /workspace/metroa-demo

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Verify FastAPI is installed
python3 -c "import fastapi; print('FastAPI OK')"

# 4. Start backend
pkill -f "python.*main.py" || true
sleep 2
cd /workspace/metroa-demo && nohup python main.py > backend.log 2>&1 &

# 5. Wait for startup
sleep 5

# 6. Check if backend is running
curl http://localhost:8888/health || curl http://localhost:8888/api/status
```

## If pip install fails

```bash
# Try with pip3
pip3 install -r requirements.txt

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt

# Or use python3 -m pip
python3 -m pip install -r requirements.txt
```

## Verify Installation

```bash
# Check installed packages
pip list | grep -i fastapi

# Test imports
python3 << 'PYTHON'
try:
    import fastapi
    import uvicorn
    import sqlite3
    print("✅ All core dependencies OK")
except ImportError as e:
    print(f"❌ Missing: {e}")
PYTHON
```
