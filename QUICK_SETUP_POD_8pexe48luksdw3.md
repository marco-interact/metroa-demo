# ⚡ Quick Setup Guide - Pod 8pexe48luksdw3

**Automated setup for new pod with same volume and configuration**

---

## 🎯 One-Command Setup

### Step 1: Access New Pod

**Option A: RunPod Web Terminal (Easiest)**
1. Go to [RunPod Dashboard](https://www.runpod.io/console/pods)
2. Find pod `8pexe48luksdw3`
3. Click "Connect" → "Web Terminal"
4. You're now in the pod terminal!

**Option B: SSH from Your Mac**
```bash
# From your Mac terminal (not from RunPod)
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519
```

**Option C: RunPod SSH Gateway**
```bash
# From your Mac terminal
ssh 8pexe48luksdw3-64411de4@ssh.runpod.io -i ~/.ssh/id_ed25519
```

### Step 2: Run Automated Setup

**☁️ RUNPOD SSH** - Copy and paste this one command:

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git && cd metroa-demo && bash setup-pod-8pexe48luksdw3.sh
```

**⏱️ Time:** 15-20 minutes (COLMAP build takes ~10-15 min)

**What it does:**
- ✅ Installs all system dependencies
- ✅ Builds COLMAP with RTX 4090 GPU support
- ✅ Sets up Python environment
- ✅ Installs Python dependencies (including Open3D)
- ✅ Configures persistent storage (same volume)
- ✅ Initializes database with demo data
- ✅ Starts backend on port 8888

**Expected Output:**
```
✨ METROA POD SETUP COMPLETE!
Backend URLs:
  • Local:  http://localhost:8888
  • Public: https://8pexe48luksdw3-8888.proxy.runpod.net
✅ READY FOR PRODUCTION!
```

---

## ✅ Step 3: Verify Backend

**📱 MAC TERMINAL** - Test backend:

```bash
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health
```

Should return:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

---

## 🌐 Step 4: Update Frontend

**📱 MAC TERMINAL** - Run automated frontend update:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
bash update-frontend-pod-8pexe48luksdw3.sh
```

**Or manually:**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
echo 'NEXT_PUBLIC_API_URL="https://8pexe48luksdw3-8888.proxy.runpod.net"' > .env.production
npm run build
vercel --prod
```

---

## 📋 Pod Details

- **Pod ID:** `8pexe48luksdw3`
- **Name:** `metroa_worker_gpu`
- **GPU:** RTX 4090 (24GB VRAM)
- **Port:** 8888 (Backend API)
- **Port:** 8888 (Jupyter Lab)
- **Volume:** `metroa-volume` (mvmh2mg1pt) - **SAME VOLUME**
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHNBJaFmISOLjiFilSH5ROHAzqyURW7j61vXnVhMebYn`
- **Jupyter Password:** `8mt1655csdm6mvvacmap`
- **SSH Gateway:** `ssh 8pexe48luksdw3-64411de4@ssh.runpod.io -i ~/.ssh/id_ed25519`
- **SSH Direct:** `ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519`
- **Public URL:** `https://8pexe48luksdw3-8888.proxy.runpod.net`
- **Jupyter Lab:** `https://8pexe48luksdw3-8888.proxy.runpod.net` (use password above)

---

## 🔧 Troubleshooting

### Backend not starting?
```bash
# On RunPod
cd /workspace/metroa-demo
tail -f backend.log

# Kill and restart
kill $(cat backend.pid)
source venv/bin/activate
python3 main.py
```

### Frontend can't connect?
- Verify backend URL: `curl https://8pexe48luksdw3-8888.proxy.runpod.net/health`
- Check `.env.production` has correct URL
- Redeploy: `vercel --prod`

---

## 📝 Notes

- **Same Volume:** Data persists from previous pod (database, scans, uploads)
- **Same GitHub Repo:** Latest code automatically pulled
- **Same Vercel Frontend:** Just needs backend URL update
- **Same Configuration:** All settings preserved

---

## ✅ Verification Checklist

- [ ] Backend health check returns `200 OK`
- [ ] API status shows demo data
- [ ] Frontend connects to new backend
- [ ] 3D viewer loads point clouds
- [ ] Previous scans/data accessible (if volume attached)

---

**Ready!** Your new pod is configured identically to the previous one. 🚀

