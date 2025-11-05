# 🚀 Deployment Quickstart - Resume CI/CD

**Issue:** Frontend can't connect to backend (502 Bad Gateway)  
**Solution:** Backend is not running on RunPod

---

## ⚡ Quick Fix (2 Steps)

### 1️⃣ Start Backend (on RunPod)

```bash
# SSH into RunPod
# Then run:
cd /workspace/colmap-demo && bash resume-runpod.sh
```

### 2️⃣ Deploy Frontend (on Local)

```bash
# On your local machine
cd /Users/marco.aurelio/Desktop/colmap-demo
bash deploy-frontend.sh
```

---

## ✅ Verify Deployment

**Test backend:**
```bash
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
```

**Expected:** `{"status":"healthy","message":"Backend is running",...}`

**Test frontend:**
- Visit: https://colmap-demo.vercel.app
- Open browser console (F12)
- Navigate to dashboard
- Should see demo projects loaded

---

## 📋 Common Commands

### Backend (RunPod SSH)

```bash
# Start backend
bash /workspace/colmap-demo/resume-runpod.sh

# Stop backend
kill $(cat /workspace/colmap-demo/backend.pid)

# View logs
tail -f /workspace/colmap-demo/backend.log

# Restart backend
kill $(cat /workspace/colmap-demo/backend.pid)
sleep 2
cd /workspace/colmap-demo && source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

### Frontend (Local)

```bash
# Quick deploy
bash deploy-frontend.sh

# Manual deploy
npm run build && vercel --prod

# Test locally
npm run dev  # http://localhost:3000
```

---

## 🔧 Troubleshooting

### Backend returns 502
- Backend not running → Run `resume-runpod.sh` on RunPod
- Pod stopped → Start pod in RunPod dashboard

### Frontend can't connect
- Check `.env.production` has correct URL
- Redeploy: `vercel --prod`

### Database empty
- Run on RunPod: `cd /workspace/colmap-demo && python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"`

---

## 📱 Monitoring URLs

- **Backend Health:** https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
- **Frontend:** https://colmap-demo.vercel.app
- **RunPod Dashboard:** https://www.runpod.io/console/pods
- **Vercel Dashboard:** https://vercel.com/interact-hq/colmap-demo

---

## 🆘 Need Help?

Read full guide: [`CICD_RESUME_GUIDE.md`](./CICD_RESUME_GUIDE.md)

