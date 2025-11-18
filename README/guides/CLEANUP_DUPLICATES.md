# Cleanup Duplicate Demo Projects

## Quick Fix Commands

```bash
# 1. Pull latest code
cd /workspace/metroa-demo && git pull origin main

# 2. Restart backend (kill existing process first)
pkill -f "python.*main.py" || true
sleep 2

# 3. Start backend
cd /workspace/metroa-demo && nohup python main.py > backend.log 2>&1 &

# 4. Wait a few seconds for startup
sleep 5

# 5. Call cleanup endpoint
curl -X POST http://localhost:8888/database/cleanup-duplicates

# 6. Verify cleanup worked
curl http://localhost:8888/api/projects?user_email=demo@metroa.app | python -m json.tool
```

## Alternative: Direct Database Cleanup

If the endpoint still doesn't work, you can run cleanup directly via Python:

```bash
cd /workspace/metroa-demo
python3 << 'PYTHON'
from database import db
result = db.cleanup_duplicate_demos()
print(f"Status: {result.get('status')}")
print(f"Deleted projects: {result.get('deleted_projects', 0)}")
print(f"Deleted scans: {result.get('deleted_scans', 0)}")
PYTHON
```

## Expected Result

After cleanup, you should have:
- ✅ 1 project: "Reconstruction Test Project 1"
- ✅ 1 scan: "Dollhouse Interior Scan"
- ❌ No "Facade Architecture Scan"
- ❌ No duplicate projects
