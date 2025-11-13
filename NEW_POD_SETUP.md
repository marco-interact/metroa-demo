# 🚀 New RunPod Pod Setup Guide

**Quick setup for a new pod after termination**

---

## ⚡ Fastest Setup (One Command)

### Step 1: Get Your New Pod Details

1. Go to [RunPod Dashboard](https://www.runpod.io/console/pods)
2. Create a new pod (or use existing one):
   - **GPU:** RTX 4090 (or similar)
   - **Container:** `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
   - **Volume:** Attach `metroa-volume` (mvmh2mg1pt) if you want to keep data
   - **Port:** Expose port `8888` (HTTP)

3. **Copy your pod details:**
   - Pod ID: `_____________` (e.g., `k0r2cn19yf6osw`)
   - SSH IP: `_____________` (e.g., `203.57.40.216`)
   - SSH Port: `_____________` (e.g., `10091`)

---

## 🎯 Step 2: Run Master Setup Script

**☁️ RUNPOD SSH** - Connect to your new pod:
```bash
ssh root@<YOUR_POD_IP> -p <YOUR_SSH_PORT> -i ~/.ssh/id_ed25519
```

**☁️ RUNPOD SSH** - Run one command:
```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git && cd metroa-demo && bash setup-metroa-pod.sh
```

**⏱️ Time:** 15-20 minutes (COLMAP build takes ~10-15 min)

**What it does:**
1. ✅ Installs all system dependencies
2. ✅ Builds COLMAP with RTX 4090 GPU support
3. ✅ Sets up Python environment (venv)
4. ✅ Installs Python dependencies (including Open3D)
5. ✅ Configures persistent storage
6. ✅ Initializes database with demo data
7. ✅ Starts backend server on port 8888

**Expected Output:**
```
✨ METROA POD SETUP COMPLETE!
Backend URLs:
  • Local:  http://localhost:8888
  • Public: https://<YOUR_POD_ID>-8888.proxy.runpod.net
✅ READY FOR PRODUCTION!
```

---

## ✅ Step 3: Verify Backend

**📱 MAC TERMINAL** - Test backend:
```bash
curl https://<YOUR_POD_ID>-8888.proxy.runpod.net/health
```

Should return:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

**📱 MAC TERMINAL** - Check demo data:
```bash
curl https://<YOUR_POD_ID>-8888.proxy.runpod.net/api/status
```

Should show: `"projects_count": 1, "scans_count": 1`

---

## 🌐 Step 4: Update Frontend Backend URL

**📱 MAC TERMINAL:**
```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Update backend URL with your new pod ID
echo 'NEXT_PUBLIC_API_URL="https://<YOUR_POD_ID>-8888.proxy.runpod.net"' > .env.production

# Deploy to Vercel
vercel --prod
```

**Or update via Vercel Dashboard:**
1. Go to https://vercel.com/interact-hq/metroa-demo/settings/environment-variables
2. Update `NEXT_PUBLIC_API_URL` to: `https://<YOUR_POD_ID>-8888.proxy.runpod.net`
3. Redeploy

---

## 🔧 Alternative: If Setup Script Fails

If the master script fails, run steps manually:

### Manual Setup (if needed)

**☁️ RUNPOD SSH:**
```bash
# 1. Install dependencies
apt-get update && apt-get install -y git python3-pip ffmpeg sqlite3

# 2. Clone repo
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Build COLMAP (if not already built)
bash build-colmap-gpu-fixed.sh

# 5. Initialize database
python3 -c "from database import db; db.setup_demo_data()"

# 6. Start backend
nohup python3 main.py > backend.log 2>&1 &
echo $! > backend.pid
```

---

## 📊 Quick Verification Checklist

- [ ] Backend health check returns `200 OK`
- [ ] API status shows demo data (1 project, 1 scan)
- [ ] Frontend connects to new backend URL
- [ ] 3D viewer loads point clouds
- [ ] Measurement tool works

---

## 💾 Data Persistence

**If you attached the `metroa-volume`:**
- ✅ Database persists (`/workspace/data/database.db`)
- ✅ Previous scan results persist (`/workspace/data/results/`)
- ✅ Uploads persist (`/workspace/data/uploads/`)

**If you didn't attach volume:**
- ⚠️ Fresh database (will recreate demo data)
- ⚠️ No previous scan results
- ⚠️ Need to re-upload videos

---

## 🆘 Troubleshooting

### Backend not starting?
```bash
# Check if port 8888 is in use
lsof -i :8888

# Kill existing process
kill $(lsof -t -i:8888)

# Restart backend
cd /workspace/metroa-demo
source venv/bin/activate
python3 main.py
```

### COLMAP not found?
```bash
# Check if COLMAP is installed
which colmap

# If not, rebuild:
cd /workspace/metroa-demo
bash build-colmap-gpu-fixed.sh
```

### Python dependencies missing?
```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend can't connect?
- Check backend URL in `.env.production`
- Verify backend is running: `curl https://<POD_ID>-8888.proxy.runpod.net/health`
- Check CORS settings in `main.py`

---

## 📝 Notes

- **Pod ID changes** when you create a new pod
- **Backend URL format:** `https://<POD_ID>-8888.proxy.runpod.net`
- **Volume attachment:** Recommended to keep data between pod restarts
- **COLMAP build:** Takes ~10-15 minutes (one-time per pod)

---

## 🎉 Done!

Your new pod should now be:
- ✅ Backend running on port 8888
- ✅ Frontend connected to new backend
- ✅ Ready for video uploads and reconstructions

**Next:** Test with a small video upload to verify everything works!

