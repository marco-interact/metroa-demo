# Debug Stuck Processing (30+ minutes on Features)

**The frontend error is fixed. Now check why processing is stuck:**

## Step 1: Check Backend Logs

**On RunPod terminal:**

```bash
# Check backend logs
tail -100 /workspace/metroa-demo/backend.log

# Check for feature extraction/matching errors
grep -i "feature\|error\|failed" /workspace/metroa-demo/backend.log | tail -50
```

## Step 2: Check Processing Status

**On RunPod terminal:**

```bash
# Check database for scan status
cd /workspace/metroa-demo && source venv/bin/activate
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/workspace/data/database.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, status, progress, current_stage FROM scans WHERE status LIKE '%processing%' OR status LIKE '%failed%' ORDER BY created_at DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"Scan: {row[1]} | Status: {row[2]} | Progress: {row[3]}% | Stage: {row[4]}")
conn.close()
EOF
```

## Step 3: Check COLMAP Process

**On RunPod terminal:**

```bash
# Check if COLMAP processes are running
ps aux | grep -E "colmap|python.*colmap" | grep -v grep

# Check GPU usage
nvidia-smi

# Check disk space
df -h /workspace
```

## Step 4: Check Specific Scan Job

**On RunPod terminal:**

```bash
# Find the scan ID from the stuck job
cd /workspace/metroa-demo && source venv/bin/activate
python3 << 'EOF'
import sqlite3
import json
conn = sqlite3.connect('/workspace/data/database.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, status, progress, current_stage FROM scans ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"Latest scan: {row[0]} | {row[1]} | Status: {row[2]} | Progress: {row[3]}% | Stage: {row[4]}")
    scan_id = row[0]
    
    # Check if there's a results directory
    import os
    results_dir = f"/workspace/data/results/{scan_id}"
    if os.path.exists(results_dir):
        print(f"\nResults directory exists: {results_dir}")
        print("Contents:")
        for item in os.listdir(results_dir):
            print(f"  - {item}")
    else:
        print(f"\nResults directory not found: {results_dir}")
conn.close()
EOF
```

## Step 5: Check Feature Extraction Progress

**On RunPod terminal:**

```bash
# Check if feature extraction database exists
SCAN_ID="<YOUR_SCAN_ID>"  # Replace with actual scan ID
ls -lh /workspace/data/results/$SCAN_ID/database.db 2>/dev/null || echo "Database not found"

# Check feature extraction logs
find /workspace/data/results/$SCAN_ID -name "*.log" -o -name "*feature*" 2>/dev/null
```

## Common Issues:

### Issue 1: Feature Extraction Taking Too Long
**Fix:** Check GPU memory and reduce max_image_size

### Issue 2: Feature Matching Failed Silently
**Fix:** Check if exhaustive matching was attempted (can fail on large datasets)

### Issue 3: Out of Memory
**Fix:** Check `nvidia-smi` and reduce batch size

### Issue 4: Database Locked
**Fix:** Kill any stuck COLMAP processes

## Quick Fix: Restart Processing

**If processing is truly stuck, you may need to:**

1. Mark scan as failed
2. Clear stuck processes
3. Retry with lower quality settings

```bash
# Kill stuck COLMAP processes
pkill -9 colmap
pkill -9 python.*colmap

# Check and restart backend
cd /workspace/metroa-demo && source venv/bin/activate
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
```

