# Metroa Deployment Guide

## New Pod Configuration

**Pod Details:**
- **Pod ID:** `k0r2cn19yf6osw`
- **Name:** metroa_worker_gpu
- **GPU:** NVIDIA RTX 4090 (24GB VRAM, Compute 8.9)
- **vCPU:** 21 cores
- **Memory:** 41 GB
- **Storage:** metroa-volume (mvmh2mg1pt)
- **Container:** runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404

**Access:**
- **Pod SSH:** `ssh k0r2cn19yf6osw-64411df8@ssh.runpod.io -i ~/.ssh/id_ed25519`
- **TCP SSH:** `ssh root@203.57.40.216 -p 10091 -i ~/.ssh/id_ed25519`

**Endpoints:**
- **Backend Port:** 8888
- **Public URL:** https://k0r2cn19yf6osw-8888.proxy.runpod.net

---

## 🚀 Step-by-Step Deployment

### Step 1: Setup RunPod Pod

**☁️ RUNPOD SSH** - Connect to pod:
```bash
ssh root@203.57.40.216 -p 10091 -i ~/.ssh/id_ed25519
```

**☁️ RUNPOD SSH** - Clone and setup:
```bash
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo
bash setup-metroa-pod.sh
```

⏱️ **Time:** 15-20 minutes (COLMAP build takes time)

**Expected Output:**
```
✨ METROA POD SETUP COMPLETE!
Backend URLs:
  • Local:  http://localhost:8888
  • Public: https://k0r2cn19yf6osw-8888.proxy.runpod.net
```

---

### Step 2: Verify Backend

**📱 MAC TERMINAL** - Test backend:
```bash
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health
```

Should return:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

**📱 MAC TERMINAL** - Check demo data:
```bash
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/api/status
```

Should show: `"projects_count": 1, "scans_count": 2`

---

### Step 3: Deploy Frontend to Vercel

**📱 MAC TERMINAL** - Create Vercel project:
```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Create .env.production
echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production

# Install dependencies
npm install

# Build
npm run build

# Deploy to Vercel (will create new project)
vercel --prod
```

When prompted:
- **Set up and deploy:** Yes
- **Scope:** interact-hq
- **Link to existing project:** No
- **Project name:** metroa-demo
- **Directory:** ./
- **Want to override settings:** No

---

### Step 4: Configure Vercel Environment

1. Go to: https://vercel.com/interact-hq/metroa-demo/settings/environment-variables
2. Add variable:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://k0r2cn19yf6osw-8888.proxy.runpod.net`
   - **Environment:** Production
3. Save and trigger redeploy

---

### Step 5: Verify Deployment

**📱 MAC TERMINAL** - Open frontend:
```bash
open https://metroa-demo.vercel.app
```

**Checklist:**
- [ ] Frontend loads without errors
- [ ] Dashboard shows "Reconstruction Test Project 1"
- [ ] 1 demo scan visible (Dollhouse)
- [ ] Can click into scans
- [ ] 3D viewer loads point clouds
- [ ] Measurement tool works (blue/green indicators)
- [ ] "Back to Scans" button works
- [ ] No console errors

---

## 🔧 Maintenance Commands

### Backend (RunPod)

**View logs:**
```bash
tail -f /workspace/metroa-demo/backend.log
```

**Restart backend:**
```bash
cd /workspace/metroa-demo
kill $(cat backend.pid) 2>/dev/null || true
source venv/bin/activate
QT_QPA_PLATFORM=offscreen DISPLAY=:99 \
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

**Update code:**
```bash
cd /workspace/metroa-demo
git pull origin main
kill $(cat backend.pid) 2>/dev/null || true
bash setup-metroa-pod.sh
```

### Frontend (Local)

**Redeploy:**
```bash
cd /path/to/metroa-demo
vercel --prod
```

**Test locally:**
```bash
npm run dev
# Visit: http://localhost:3000
```

---

## 📊 Monitoring

### Backend Health
```bash
# Every 30 seconds
watch -n 30 'curl -s https://k0r2cn19yf6osw-8888.proxy.runpod.net/health'
```

### GPU Usage
```bash
# On RunPod
watch -n 2 nvidia-smi
```

### Processing Jobs
```bash
# View active scans
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/api/status
```

---

## 🎯 Success Criteria

✅ **Backend:**
- Health check returns 200
- Demo data loaded (1 project, 1 scan)
- GPU detected (or CPU fallback active)
- Logs show no errors

✅ **Frontend:**
- Deploys to Vercel successfully
- Connects to backend
- Dashboard loads projects
- 3D viewer renders point clouds
- Measurement tool functional

✅ **Integration:**
- Video upload works
- Processing completes in < 3 minutes
- Dense point clouds generated
- Measurements accurate

---

## 📝 Notes

- **Persistent Storage:** All data in `/workspace/data/` (on volume)
- **Database:** `/workspace/data/database.db` (persistent)
- **Backups:** Stored on RunPod volume (survives pod restarts)
- **GPU:** Auto-fallback to CPU if GPU fails
- **Port:** Changed from 8000 → 8888

---

**Deployment by:** AI Assistant  
**Date:** November 12, 2025  
**Status:** Production Ready ✅

