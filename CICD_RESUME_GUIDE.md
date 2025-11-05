# CI/CD Resume Guide - RunPod + Vercel Deployment

**Date:** November 5, 2025  
**Issue:** Frontend failing to connect to backend (502 Bad Gateway)  
**Root Cause:** Backend server not running on RunPod pod

## Problem Summary

The frontend (deployed on Vercel) is trying to connect to the backend on RunPod at:
```
https://xhqt6a1roo8mrc-8000.proxy.runpod.net
```

However, the backend is returning a **502 Bad Gateway** error, which means:
- The RunPod pod is running, but the backend service is not started
- OR the pod has been paused/stopped

## Solution: Two-Step Deployment

### Step 1: Start Backend on RunPod

**SSH into your RunPod instance:**

```bash
# Find your pod connection details in RunPod dashboard
# Pod ID: xhqt6a1roo8mrc
# Or get new connection command from RunPod web interface
```

**Run the resume script:**

```bash
cd /workspace/colmap-demo
bash resume-runpod.sh
```

This script will:
1. ✅ Pull latest code from GitHub
2. ✅ Update Python dependencies
3. ✅ Verify COLMAP installation
4. ✅ Initialize database with demo data
5. ✅ Start backend server on port 8000
6. ✅ Display public URL

**Verify backend is running:**

```bash
# On RunPod pod
curl http://localhost:8000/health

# From your local machine
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
```

Expected response:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/database.db"}
```

---

### Step 2: Deploy Frontend to Vercel

**On your LOCAL machine:**

```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
bash deploy-frontend.sh
```

This script will:
1. ✅ Test backend connectivity
2. ✅ Install npm dependencies
3. ✅ Build Next.js application
4. ✅ Test build locally (optional)
5. ✅ Deploy to Vercel production

---

## Manual Deployment (Alternative)

If the automated scripts don't work, follow these manual steps:

### Manual Backend Deployment

```bash
# SSH into RunPod
ssh root@YOUR_POD_IP

# Navigate to project
cd /workspace/colmap-demo

# Pull latest code
git pull origin main

# Activate Python environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Kill existing server
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start server
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Save PID
echo $! > backend.pid

# Test
curl http://localhost:8000/health
```

### Manual Frontend Deployment

```bash
# On your local machine
cd /Users/marco.aurelio/Desktop/colmap-demo

# Update .env.production with correct backend URL
echo 'NEXT_PUBLIC_API_URL="https://xhqt6a1roo8mrc-8000.proxy.runpod.net"' > .env.production

# Install dependencies
npm install

# Build
npm run build

# Deploy to Vercel
vercel --prod --yes
```

---

## Vercel Environment Variables

Make sure these are set in your Vercel project settings:

1. Go to: https://vercel.com/interact-hq/colmap-demo/settings/environment-variables
2. Add/Update:
   - **Variable:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://xhqt6a1roo8mrc-8000.proxy.runpod.net`
   - **Environment:** Production

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                                                              │
│  Frontend: Next.js App (hosted on Vercel)                   │
│  URL: https://colmap-demo.vercel.app                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ API Requests to /api/backend/*
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Next.js API Rewrites                      │
│                                                              │
│  /api/backend/* → https://POD_ID-8000.proxy.runpod.net/api/*│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Proxied to RunPod
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    RunPod Backend                            │
│                                                              │
│  Pod ID: xhqt6a1roo8mrc                                     │
│  Public URL: https://xhqt6a1roo8mrc-8000.proxy.runpod.net   │
│  Internal: http://0.0.0.0:8000                              │
│                                                              │
│  Components:                                                 │
│  - FastAPI server (main.py)                                 │
│  - COLMAP GPU processing                                    │
│  - SQLite database                                          │
│  - File storage (/workspace/data)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files

### Frontend Configuration

- **next.config.js** - API rewrites configuration
  ```javascript
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/backend/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  }
  ```

- **.env.production** - Production environment variables
  ```bash
  NEXT_PUBLIC_API_URL="https://xhqt6a1roo8mrc-8000.proxy.runpod.net"
  ```

- **src/lib/api.ts** - API client
  ```typescript
  const getWorkerUrl = () => {
    return '/api/backend'  // Uses Next.js proxy
  }
  ```

### Backend Configuration

- **main.py** - FastAPI application
  - CORS enabled for all origins
  - Serves static files from `/demo-resources` and `/results`
  - Database at `/workspace/database.db`

- **runpod-setup.sh** - Initial setup script
- **resume-runpod.sh** - Resume/restart script (NEW)

---

## Troubleshooting

### Backend Issues

**502 Bad Gateway**
```bash
# Problem: Backend server not running
# Solution: Start backend on RunPod
bash /workspace/colmap-demo/resume-runpod.sh
```

**Database not initialized**
```bash
# Reinitialize database
cd /workspace/colmap-demo
source venv/bin/activate
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
```

**COLMAP not found**
```bash
# Reinstall COLMAP
bash /workspace/colmap-demo/runpod-install-colmap.sh
```

### Frontend Issues

**Can't connect to backend**
```bash
# 1. Check backend URL in .env.production
cat .env.production

# 2. Test backend connection
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health

# 3. Check Vercel environment variables
vercel env ls

# 4. Redeploy with correct variables
vercel --prod
```

**CORS errors**
- Backend should have `allow_origins=["*"]` in CORS middleware (already configured)
- Check browser console for specific CORS errors

### RunPod Pod Issues

**Pod stopped/paused**
- Go to RunPod dashboard
- Start/resume the pod
- Wait for it to be ready
- SSH in and run `resume-runpod.sh`

**Pod ID changed**
- Get new pod ID from RunPod dashboard
- Update `.env.production`:
  ```bash
  NEXT_PUBLIC_API_URL="https://NEW_POD_ID-8000.proxy.runpod.net"
  ```
- Redeploy frontend

**Out of GPU credits**
- Add credits to RunPod account
- Or switch to CPU-only processing (slower)

---

## Monitoring

### Backend Logs

```bash
# On RunPod pod
tail -f /workspace/colmap-demo/backend.log
```

### Backend Status

```bash
# Check if running
ps aux | grep uvicorn

# Check PID
cat /workspace/colmap-demo/backend.pid
```

### Stop Backend

```bash
# On RunPod pod
kill $(cat /workspace/colmap-demo/backend.pid)
```

### Restart Backend

```bash
# On RunPod pod
kill $(cat /workspace/colmap-demo/backend.pid)
bash /workspace/colmap-demo/resume-runpod.sh
```

---

## Quick Reference Commands

### Backend Commands (RunPod)

```bash
# Start backend
bash /workspace/colmap-demo/resume-runpod.sh

# Stop backend
kill $(cat /workspace/colmap-demo/backend.pid)

# View logs
tail -f /workspace/colmap-demo/backend.log

# Test locally
curl http://localhost:8000/health

# Test publicly
POD_ID=$(hostname)
curl https://${POD_ID}-8000.proxy.runpod.net/health
```

### Frontend Commands (Local)

```bash
# Deploy frontend
bash /Users/marco.aurelio/Desktop/colmap-demo/deploy-frontend.sh

# Or manual deployment
npm install
npm run build
vercel --prod

# Test locally
npm run dev  # http://localhost:3000
```

---

## Success Criteria

✅ Backend health check returns 200:
```bash
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
# {"status":"healthy",...}
```

✅ Frontend loads successfully:
```
https://colmap-demo.vercel.app
```

✅ Frontend can fetch projects:
- Open browser console
- Navigate to dashboard
- Should see API requests succeeding

✅ Demo data visible:
- Should see "Reconstruction Test Project 1"
- Should see demo scans: demoscan-dollhouse, demoscan-fachada

---

## Next Steps After Successful Deployment

1. **Test video upload**: Upload a test video and monitor processing
2. **Monitor GPU usage**: Check RunPod dashboard for GPU utilization
3. **Set up monitoring**: Consider adding uptime monitoring for the backend
4. **Database backups**: Set up periodic backups of `/workspace/database.db`
5. **Cost optimization**: Monitor RunPod costs and consider autoscaling

---

## Support Resources

- **RunPod Dashboard**: https://www.runpod.io/console/pods
- **Vercel Dashboard**: https://vercel.com/interact-hq/colmap-demo
- **GitHub Repository**: https://github.com/marco-interact/colmap-demo
- **COLMAP Documentation**: https://colmap.github.io/

---

## Contact

For issues or questions, contact the development team or refer to the project documentation in `/cursor-logs/`.

