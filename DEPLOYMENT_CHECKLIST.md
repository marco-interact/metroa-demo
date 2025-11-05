# ✅ Deployment Checklist - Resume CI/CD

**Date:** November 5, 2025  
**Current Status:** Backend offline (502), Frontend deployed but can't connect

---

## Pre-Deployment Check

- [x] Issue identified: Backend not running on RunPod
- [x] Scripts created: `resume-runpod.sh` and `deploy-frontend.sh`
- [x] Environment variables verified: `.env.production` has correct URL
- [x] Documentation created: Full deployment guide available

---

## Part 1: Start Backend on RunPod

### Access RunPod

- [ ] Open RunPod dashboard: https://www.runpod.io/console/pods
- [ ] Locate pod: `xhqt6a1roo8mrc` (colmap_worker_gpu)
- [ ] Ensure pod is **Running** (not Stopped or Paused)
- [ ] Click "Connect" to get SSH command

### SSH into RunPod

```bash
# Copy SSH command from RunPod dashboard, should look like:
ssh root@<pod-ip> -p <port> -i <key-file>

# Or use RunPod's web terminal
```

### Run Deployment Script

```bash
# Navigate to project
cd /workspace/colmap-demo

# Pull latest code (includes resume script)
git pull origin main

# Run resume script
bash resume-runpod.sh
```

**Expected Output:**
```
✨ RunPod Backend Deployment Complete!
📋 Backend Status:
   • Server PID: <pid>
   • Local URL: http://localhost:8000
   • Public URL: https://xhqt6a1roo8mrc-8000.proxy.runpod.net
```

### Verify Backend

- [ ] Check health endpoint locally (on RunPod):
```bash
curl http://localhost:8000/health
```

- [ ] Check health endpoint publicly (from anywhere):
```bash
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Backend is running",
  "database_path": "/workspace/database.db"
}
```

- [ ] Check backend logs (if needed):
```bash
tail -f /workspace/colmap-demo/backend.log
```

**Backend Checklist:**
- [ ] ✅ Backend responds to /health
- [ ] ✅ No errors in backend.log
- [ ] ✅ Database initialized with demo data
- [ ] ✅ COLMAP is accessible

---

## Part 2: Deploy Frontend to Vercel

### On Your Local Machine

```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
```

### Option A: Automated Deployment (Recommended)

```bash
bash deploy-frontend.sh
```

The script will:
1. Test backend connectivity
2. Install dependencies
3. Build frontend
4. Deploy to Vercel

### Option B: Manual Deployment

```bash
# 1. Verify environment
cat .env.production
# Should show: NEXT_PUBLIC_API_URL="https://xhqt6a1roo8mrc-8000.proxy.runpod.net"

# 2. Test backend
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health

# 3. Install dependencies
npm install

# 4. Build
npm run build

# 5. Deploy
vercel --prod --yes
```

### Update Vercel Environment Variables

- [ ] Go to: https://vercel.com/interact-hq/colmap-demo/settings/environment-variables
- [ ] Verify `NEXT_PUBLIC_API_URL` is set to: `https://xhqt6a1roo8mrc-8000.proxy.runpod.net`
- [ ] If not set or incorrect, add/update it
- [ ] Make sure it's enabled for **Production** environment
- [ ] Trigger a new deployment if you changed the variable

**Frontend Checklist:**
- [ ] ✅ Build completes without errors
- [ ] ✅ Vercel deployment succeeds
- [ ] ✅ Environment variable set correctly

---

## Part 3: Verify End-to-End Deployment

### Test Frontend Access

- [ ] Open frontend: https://colmap-demo.vercel.app
- [ ] Open browser console (F12 → Console tab)
- [ ] Refresh page

### Check for Errors

**In Browser Console, look for:**
- [ ] No CORS errors
- [ ] No 502 errors
- [ ] API requests to `/api/backend/*` should succeed

**Expected console output:**
```
🔍 Using Next.js API proxy: { url: '/api/backend', timestamp: '...' }
📊 Loaded N scans for project <project-id>
```

### Test Dashboard

- [ ] Navigate to Dashboard
- [ ] Should see "Reconstruction Test Project 1"
- [ ] Click on the project
- [ ] Should see demo scans:
  - demoscan-dollhouse
  - demoscan-fachada

### Test 3D Viewer

- [ ] Click on a demo scan
- [ ] 3D viewer should load
- [ ] Point cloud should display
- [ ] No loading errors in console

**End-to-End Checklist:**
- [ ] ✅ Frontend loads successfully
- [ ] ✅ Dashboard displays projects
- [ ] ✅ Demo data visible
- [ ] ✅ 3D viewer works
- [ ] ✅ No console errors

---

## Part 4: Test Upload (Optional)

### Upload Test Video

- [ ] Navigate to a project
- [ ] Click "New Scan"
- [ ] Upload a test video (MP4, < 500MB)
- [ ] Submit

### Monitor Processing

- [ ] Processing status should update:
  - Queued → Extracting Frames → Extracting Features → Matching Features → Reconstructing → Complete

- [ ] Check backend logs on RunPod:
```bash
tail -f /workspace/colmap-demo/backend.log
```

**Upload Test Checklist:**
- [ ] ✅ Video uploads successfully
- [ ] ✅ Processing starts
- [ ] ✅ Status updates in real-time
- [ ] ✅ Scan completes (or progresses as expected)

---

## Troubleshooting

### If Backend Health Check Fails

**Problem:** `curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health` returns 502

**Solutions:**
1. Check if backend is running on RunPod:
   ```bash
   ps aux | grep uvicorn
   ```

2. Restart backend:
   ```bash
   cd /workspace/colmap-demo
   bash resume-runpod.sh
   ```

3. Check backend logs:
   ```bash
   tail -f /workspace/colmap-demo/backend.log
   ```

### If Frontend Shows Errors

**Problem:** Console shows network errors or CORS errors

**Solutions:**
1. Verify `.env.production`:
   ```bash
   cat /Users/marco.aurelio/Desktop/colmap-demo/.env.production
   ```

2. Verify Vercel environment variables:
   - Go to Vercel dashboard
   - Check environment variables
   - Redeploy if needed

3. Test backend directly:
   ```bash
   curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/api/status
   ```

### If Pod ID Changed

**Problem:** RunPod assigned a new pod ID

**Solution:**
1. Get new pod ID from RunPod dashboard

2. Update `.env.production`:
   ```bash
   echo 'NEXT_PUBLIC_API_URL="https://NEW_POD_ID-8000.proxy.runpod.net"' > .env.production
   ```

3. Update Vercel environment variables

4. Redeploy:
   ```bash
   vercel --prod
   ```

### If Database is Empty

**Problem:** No demo data visible

**Solution:**
1. SSH into RunPod

2. Reinitialize database:
   ```bash
   cd /workspace/colmap-demo
   source venv/bin/activate
   python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
   ```

3. Restart backend:
   ```bash
   bash resume-runpod.sh
   ```

---

## Success Criteria

✅ **All checks must pass:**

| Component | Check | Status |
|-----------|-------|--------|
| Backend | Health endpoint returns 200 | ⬜ |
| Backend | Demo data in database | ⬜ |
| Backend | COLMAP available | ⬜ |
| Frontend | Deploys to Vercel | ⬜ |
| Frontend | Loads without errors | ⬜ |
| Integration | Dashboard shows projects | ⬜ |
| Integration | 3D viewer works | ⬜ |
| Integration | No console errors | ⬜ |

---

## Post-Deployment

### Monitor Performance

- [ ] Check RunPod GPU usage
- [ ] Monitor Vercel bandwidth
- [ ] Set up error tracking (optional)

### Cost Monitoring

- [ ] Review RunPod pod costs
- [ ] Set up billing alerts (optional)
- [ ] Consider auto-pause for pod when inactive

### Documentation

- [ ] Update team on deployment status
- [ ] Document any issues encountered
- [ ] Update runbook if needed

---

## Quick Command Reference

```bash
# Backend Commands (RunPod SSH)
bash /workspace/colmap-demo/resume-runpod.sh  # Start backend
kill $(cat /workspace/colmap-demo/backend.pid)  # Stop backend
tail -f /workspace/colmap-demo/backend.log  # View logs

# Frontend Commands (Local)
bash /Users/marco.aurelio/Desktop/colmap-demo/deploy-frontend.sh  # Deploy
npm run dev  # Test locally
vercel --prod  # Manual deploy

# Health Checks
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health  # Backend
curl https://colmap-demo.vercel.app  # Frontend
```

---

## Support

- **Full Guide:** [`CICD_RESUME_GUIDE.md`](./CICD_RESUME_GUIDE.md)
- **Quick Start:** [`DEPLOYMENT_QUICKSTART.md`](./DEPLOYMENT_QUICKSTART.md)
- **RunPod Dashboard:** https://www.runpod.io/console/pods
- **Vercel Dashboard:** https://vercel.com/interact-hq/colmap-demo

---

**Deployment prepared by:** AI Assistant  
**Date:** November 5, 2025  
**Status:** Ready for deployment ✅

