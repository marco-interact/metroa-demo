# Debug Backend Health Check

## Step 1: Check if Backend Process is Running

```bash
ps aux | grep "python.*main.py" | grep -v grep
```

If nothing shows, the backend isn't running.

## Step 2: Check if Port 8888 is in Use

```bash
lsof -i :8888
# or
netstat -tulpn | grep 8888
```

## Step 3: Try Starting Backend in Foreground (to see errors)

```bash
cd /workspace/metroa-demo
python main.py
```

This will show any startup errors. Press Ctrl+C to stop.

## Step 4: Check Backend Logs

If you started with nohup:
```bash
tail -f backend.log
```

If you started with screen:
```bash
screen -r metroa-backend
```

## Step 5: Check Python Dependencies

```bash
cd /workspace/metroa-demo
python3 -c "import fastapi; print('FastAPI OK')"
python3 -c "import uvicorn; print('Uvicorn OK')"
```

## Step 6: Check Database

```bash
ls -lh /workspace/database.db
```

## Step 7: Try Different Port

If port 8888 is blocked, try port 8000:
```bash
PORT=8000 python main.py
```

Then test:
```bash
curl http://localhost:8000/health
```

## Common Issues

### Backend Not Starting
- Check Python version: `python3 --version` (should be 3.12+)
- Install dependencies: `pip install --break-system-packages -r requirements.txt`
- Check for syntax errors: `python3 -m py_compile main.py`

### Port Already in Use
```bash
# Find what's using port 8888
lsof -i :8888
# Kill it
kill -9 <PID>
```

### Database Issues
```bash
# Check database file
ls -lh /workspace/database.db
# Check permissions
chmod 644 /workspace/database.db
```

### Import Errors
```bash
# Test imports
python3 -c "from colmap_binary_parser import MeasurementSystem; print('OK')"
python3 -c "from database import Database; print('OK')"
```

