# Fix Blinker Installation Issue

## Problem
`blinker` is a system package installed by Debian, and pip can't uninstall it. This blocks installation.

## Solution: Install with --break-system-packages or --ignore-installed

```bash
cd /workspace/metroa-demo

# Option 1: Use --break-system-packages (Python 3.12+)
pip install --break-system-packages -r requirements.txt

# Option 2: Use --ignore-installed for blinker specifically
pip install --ignore-installed blinker -r requirements.txt

# Option 3: Install to user directory (safer)
pip install --user -r requirements.txt

# Option 4: Skip blinker and install rest
pip install -r requirements.txt --ignore-installed blinker
```

## After Installation

```bash
# Verify FastAPI is installed
python3 -c "import fastapi; print('FastAPI OK')"

# Start backend
cd /workspace/metroa-demo
pkill -f "python.*main.py" || true
sleep 2
nohup python main.py > backend.log 2>&1 &

# Wait and check
sleep 5
curl http://localhost:8888/health || curl http://localhost:8888/api/status
```

## If Still Failing

Try installing core dependencies first:

```bash
cd /workspace/metroa-demo

# Install core dependencies only
pip install --break-system-packages fastapi uvicorn[standard] python-multipart aiosqlite

# Then install rest
pip install --break-system-packages -r requirements.txt
```
