# 🚀 Deployment Commands

## ✅ Changes Pushed to GitHub

Repository: `https://github.com/marco-interact/metroa-demo.git`

**Latest commit:** Storage optimization (removed build artifacts, cleaned git history)

---

## 📦 RunPod Backend - Pull & Update

### Option 1: Update Existing Pod

```bash
# SSH into RunPod pod
ssh root@<POD_IP> -p <PORT> -i ~/.ssh/id_ed25519

# Navigate to project directory
cd /workspace/metroa-demo

# Pull latest changes
git pull metroa main
# or if using origin:
git pull origin main

# If you have local changes, stash them first:
git stash
git pull metroa main
git stash pop

# Restart backend (if running)
pkill -f "python.*main.py" || pkill -f "uvicorn.*main:app"
cd /workspace/metroa-demo
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Verify backend is running
curl http://localhost:8888/health
```

### Option 2: Fresh Setup (New Pod)

```bash
# SSH into RunPod pod
ssh root@<POD_IP> -p <PORT> -i ~/.ssh/id_ed25519

# Clone repository
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# Run setup script (installs dependencies, builds COLMAP, starts backend)
bash setup-metroa-pod.sh

# Verify backend is running
curl http://localhost:8888/health
```

### Option 3: Quick Update (No Backend Restart Needed)

```bash
# SSH into RunPod pod
cd /workspace/metroa-demo

# Pull latest code
git pull metroa main

# Backend will auto-reload if --reload flag is used
# Check logs to verify
tail -f backend.log
```

---

## 🌐 Vercel Frontend - Deploy

### Option 1: Deploy from Local Machine

```bash
# Navigate to project directory
cd /Users/marco.aurelio/Desktop/metroa-demo

# Install dependencies (if not already installed)
npm install

# Set backend URL (replace with your RunPod pod URL)
echo 'NEXT_PUBLIC_API_URL="https://<POD_ID>-8888.proxy.runpod.net"' > .env.production

# Deploy to Vercel
vercel --prod

# When prompted:
# - Scope: interact-hq
# - Link to existing: Yes (if updating existing project)
# - Project name: metroa-demo
# - Directory: ./
# - Override settings: No
```

### Option 2: Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select project: `metroa-demo`
3. Go to **Settings** → **Environment Variables**
4. Add/Update: `NEXT_PUBLIC_API_URL` = `https://<POD_ID>-8888.proxy.runpod.net`
5. Go to **Deployments** → Click **Redeploy** on latest deployment
6. Or push to GitHub (Vercel will auto-deploy if connected)

### Option 3: Auto-Deploy from GitHub (Recommended)

If Vercel is connected to GitHub:

1. **Push changes trigger auto-deploy:**
   ```bash
   git push metroa main
   ```

2. **Vercel will automatically:**
   - Detect the push
   - Install dependencies (`npm install`)
   - Build the project (`npm run build`)
   - Deploy to production

3. **Set Environment Variable in Vercel Dashboard:**
   - Go to: Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://<POD_ID>-8888.proxy.runpod.net`
   - Apply to: Production, Preview, Development

---

## 🔍 Verify Deployment

### Backend Health Check

```bash
# Replace <POD_ID> with your actual RunPod pod ID
curl https://<POD_ID>-8888.proxy.runpod.net/health

# Expected response:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

### Frontend Check

1. Open: `https://metroa-demo.vercel.app`
2. Login with demo credentials:
   - Email: `demo@metroa.app`
   - Password: `demo123`
3. Verify features:
   - ✅ Dashboard loads
   - ✅ 3D viewer displays point clouds
   - ✅ Measurement tool works
   - ✅ Video upload works

---

## 📝 Quick Reference

### RunPod Pod Details
- **Repository**: `https://github.com/marco-interact/metroa-demo.git`
- **Remote name**: `metroa` (or `origin`)
- **Branch**: `main`
- **Backend port**: `8888`
- **Backend URL format**: `https://<POD_ID>-8888.proxy.runpod.net`

### Vercel Project Details
- **Project name**: `metroa-demo`
- **Team**: `interact-hq`
- **Frontend URL**: `https://metroa-demo.vercel.app`
- **Environment variable**: `NEXT_PUBLIC_API_URL`

### Common Commands

```bash
# RunPod - Check backend status
curl http://localhost:8888/health

# RunPod - View backend logs
tail -f /workspace/metroa-demo/backend.log

# RunPod - Restart backend
pkill -f "uvicorn.*main:app"
cd /workspace/metroa-demo && source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Local - Build frontend (for testing)
npm run build

# Local - Run frontend dev server
npm run dev
```

---

## 🆘 Troubleshooting

### RunPod Issues

**Backend not responding:**
```bash
# Check if process is running
ps aux | grep uvicorn

# Check logs
tail -50 /workspace/metroa-demo/backend.log

# Restart backend
cd /workspace/metroa-demo
source venv/bin/activate
pkill -f "uvicorn.*main:app"
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
```

**Git pull conflicts:**
```bash
# Stash local changes
git stash

# Pull latest
git pull metroa main

# Apply stashed changes
git stash pop

# Resolve conflicts if any
```

### Vercel Issues

**Build fails:**
- Check Vercel build logs in dashboard
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Verify `package.json` dependencies are correct

**Environment variable not working:**
- Ensure variable name is exactly: `NEXT_PUBLIC_API_URL`
- Redeploy after adding/updating variable
- Check variable is set for Production environment

---

## 📚 Additional Resources

- [README.md](./README.md) - Full project documentation
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
- [setup-metroa-pod.sh](./setup-metroa-pod.sh) - RunPod setup script
