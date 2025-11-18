# 🚀 RunPod Deployment Commands

## Quick Reference for RunPod Web Terminal

### 📥 Pull Latest Code

```bash
# Navigate to workspace
cd /workspace/metroa-demo

# Pull latest changes from GitHub
git pull origin main

# Verify files updated
git log --oneline -3
```

**Expected Output**:
```
Updating 48c930f..07a7915
Fast-forward
 DEPLOY_ADVANCED_FPS.md                      | 280 ++++++++++++
 FPS_VIEWER_ADVANCED.md                      | 456 +++++++++++++++++
 IMPLEMENTATION_SUMMARY.md                   | 544 +++++++++++++++++++++
 src/components/3d/FirstPersonViewer.tsx     | 841 ++++++++++++++++++++-----------
 src/utils/octree.ts                         | 338 +++++++++++++
 5 files changed, 2135 insertions(+), 324 deletions(-)
```

---

## 🔄 Restart Backend (If Needed)

### Check If Backend Is Running

```bash
# Check port 8888
curl http://localhost:8888/health

# If you get connection refused, backend is down
```

### Kill Existing Processes

```bash
# Find and kill any process on port 8888
lsof -ti:8888 | xargs kill -9

# Kill any existing Docker containers
docker ps -q | xargs -r docker kill
```

### Start Backend

```bash
# Ensure Docker daemon is running
dockerd > /dev/null 2>&1 &
sleep 3

# Navigate to workspace
cd /workspace/metroa-demo

# Build Docker image
docker build -t metroa-backend .

# Run Docker container
docker run -d \
  --name metroa-backend \
  --gpus all \
  -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend

# Wait for backend to start
sleep 10

# Test backend
curl http://localhost:8888/health
```

**Expected Output**:
```json
{"status":"healthy","message":"Server is running","gpu_available":true}
```

---

## 🧪 Test Backend Endpoints

```bash
# Health check
curl http://localhost:8888/health

# List projects
curl http://localhost:8888/api/projects

# Check specific scan
curl http://localhost:8888/api/scans/SCAN_ID
```

---

## 📊 Check Logs

```bash
# View Docker logs (last 50 lines)
docker logs metroa-backend --tail 50

# Follow logs in real-time
docker logs -f metroa-backend

# Check for errors
docker logs metroa-backend 2>&1 | grep -i error
```

---

## 🔍 Verify Files

```bash
# Check new files exist
ls -la /workspace/metroa-demo/src/utils/octree.ts
ls -la /workspace/metroa-demo/src/components/3d/FirstPersonViewer.tsx

# Check documentation
ls -la /workspace/metroa-demo/*.md
```

---

## ⚡ Quick Troubleshooting

### Backend Won't Start

```bash
# Kill everything and restart
pkill -f uvicorn
lsof -ti:8888 | xargs kill -9
docker ps -q | xargs -r docker kill

# Restart from scratch
cd /workspace/metroa-demo
docker build -t metroa-backend .
docker run -d --name metroa-backend --gpus all -p 8888:8888 -v /workspace/metroa-demo/data:/workspace/data metroa-backend
sleep 10
curl http://localhost:8888/health
```

### Port 8888 Already in Use

```bash
# Find what's using port 8888
lsof -i:8888

# Kill it
lsof -ti:8888 | xargs kill -9

# If it's Jupyter, stop it
jupyter notebook stop 8888
```

### Docker Issues

```bash
# Restart Docker daemon
pkill dockerd
sleep 2
dockerd > /dev/null 2>&1 &
sleep 3

# Clean up Docker
docker system prune -f

# Remove old containers
docker rm -f metroa-backend
```

---

## 🎯 Complete Restart Sequence

**Use this if everything is broken**:

```bash
# 1. Kill everything
pkill -f uvicorn
pkill -f python
lsof -ti:8888 | xargs kill -9
docker ps -q | xargs -r docker kill
docker system prune -f

# 2. Restart Docker
pkill dockerd
sleep 2
dockerd > /dev/null 2>&1 &
sleep 3

# 3. Pull latest code
cd /workspace/metroa-demo
git pull origin main

# 4. Rebuild and run
docker build -t metroa-backend .
docker run -d \
  --name metroa-backend \
  --gpus all \
  -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend

# 5. Wait and test
sleep 15
curl http://localhost:8888/health
```

---

## 📝 Notes

### Frontend-Only Changes
- The latest updates are **frontend-only** (First Person Viewer)
- Backend does **not** need to be restarted
- You only need to pull the latest code: `git pull origin main`

### When to Restart Backend
- After changes to Python files in `/backend`
- After changes to `Dockerfile` or `requirements.txt`
- If backend is crashed or unresponsive
- If you see "Connection refused" errors

### Frontend Deployment
- Frontend is deployed on Vercel
- Changes are live at: https://metroa-demo-1y4ab2589-interact-hq.vercel.app
- No action needed on RunPod for frontend changes

---

## 🆘 Help

If you see errors, check:

1. **Docker daemon running**: `ps aux | grep dockerd`
2. **Port 8888 free**: `lsof -i:8888`
3. **Git status**: `git status` and `git log -1`
4. **Backend logs**: `docker logs metroa-backend --tail 20`

---

## ✅ Success Checklist

- [ ] Git pull completed without errors
- [ ] New files visible in `/workspace/metroa-demo`
- [ ] Backend responds to health check (if needed to restart)
- [ ] No errors in Docker logs
- [ ] Can access frontend at Vercel URL

---

**Last Updated**: November 18, 2025  
**Version**: Advanced FPS Viewer v2.0  
**Status**: Frontend-only changes, backend restart optional

