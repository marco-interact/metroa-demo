# 🚀 CI/CD Deployment Instructions - With Location Labels

**Last Updated:** November 5, 2025  
**Status:** Scripts pushed to GitHub, ready to deploy

---

## 📍 Important: Command Location Labels

Every command in this guide is labeled with WHERE to run it:

- **📱 MAC TERMINAL** = Your Mac's terminal application
- **☁️ RUNPOD WEB TERMINAL** = RunPod's web-based terminal (or SSH)
- **💻 CURSOR TERMINAL** = Terminal inside Cursor IDE

---

## Step 1: Start Backend on RunPod

### 1.1 Access RunPod Terminal

**📱 MAC TERMINAL** - Open RunPod dashboard:
```bash
# Open in browser:
open https://www.runpod.io/console/pods
```

Then:
1. Find your pod: `xhqt6a1roo8mrc` (colmap_worker_gpu)
2. Click the **"Connect"** button
3. Click **"Start Web Terminal"** or copy the SSH command

### 1.2 Pull Latest Code

**☁️ RUNPOD WEB TERMINAL** - Run these commands:
```bash
cd /workspace/colmap-demo
git pull origin main
```

Expected output:
```
remote: Enumerating objects: 13, done.
...
Updating 6213010a..10023eb4
Fast-forward
 7 files changed, 1684 insertions(+)
 create mode 100755 resume-runpod.sh
 ...
```

### 1.3 Run Backend Startup Script

**☁️ RUNPOD WEB TERMINAL** - Run this command:
```bash
bash resume-runpod.sh
```

Expected output:
```
==================================================
🚀 Starting RunPod COLMAP Setup
==================================================

==> Step 1/6: Pulling latest code from GitHub...
✅ Code updated

==> Step 2/6: Updating Python dependencies...
✅ Python dependencies updated

==> Step 3/6: Verifying COLMAP installation...
✅ COLMAP installed: COLMAP 3.x

==> Step 4/6: Initializing database...
✅ Database initialized successfully!
✅ Database initialized

==> Step 5/6: Starting backend server...
✅ Backend server started successfully!

==================================================
✨ RunPod Backend Deployment Complete!
==================================================

📋 Backend Status:
   • Server PID: 12345
   • Local URL: http://localhost:8000
   • Public URL: https://19f2f827da7c-8000.proxy.runpod.net
```

### 1.4 Verify Backend is Running

**☁️ RUNPOD WEB TERMINAL** - Test locally:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/database.db"}
```

**📱 MAC TERMINAL** - Test publicly (from your Mac):
```bash
# Replace POD_ID with your actual pod ID from the output above
curl https://19f2f827da7c-8000.proxy.runpod.net/health
```

Should return the same JSON response.

### 1.5 Check Backend Logs (Optional)

**☁️ RUNPOD WEB TERMINAL** - View logs:
```bash
tail -f /workspace/colmap-demo/backend.log
```

Press `Ctrl+C` to stop viewing logs.

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Update Environment Variable (If Pod ID Changed)

**📱 MAC TERMINAL** - Check current .env.production:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
cat .env.production
```

If your pod ID changed from `xhqt6a1roo8mrc` to something else (like `19f2f827da7c`), update it:

**📱 MAC TERMINAL** - Update the URL:
```bash
# Replace NEW_POD_ID with your actual pod ID
echo 'NEXT_PUBLIC_API_URL="https://NEW_POD_ID-8000.proxy.runpod.net"' > .env.production
```

### 2.2 Run Frontend Deployment Script

**📱 MAC TERMINAL** - Deploy to Vercel:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
bash deploy-frontend.sh
```

The script will:
1. ✅ Test backend connection
2. ✅ Install npm dependencies
3. ✅ Build Next.js application
4. ✅ Deploy to Vercel
5. ✅ Show deployment URL

Expected output:
```
==================================================
🚀 Deploying Frontend to Vercel
==================================================

==> Step 1/5: Verifying backend connection...
ℹ  Backend URL: https://19f2f827da7c-8000.proxy.runpod.net
ℹ  Testing backend connection...
ℹ  ✅ Backend is responding (HTTP 200)

==> Step 2/5: Installing dependencies...
✅ Dependencies installed

==> Step 3/5: Building frontend...
✅ Frontend built successfully

==> Step 4/5: Testing build locally...
✅ Local server running

==> Step 5/5: Deploying to Vercel...
✅ Deployment complete!

==================================================
✨ Frontend Deployment Complete!
==================================================
```

### 2.3 Alternative: Manual Deployment

If the script doesn't work, deploy manually:

**📱 MAC TERMINAL** - Manual steps:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo

# Install dependencies
npm install

# Build
npm run build

# Deploy
vercel --prod --yes
```

---

## Step 3: Verify Deployment

### 3.1 Test Backend Health

**📱 MAC TERMINAL** - Check backend:
```bash
# Replace with your pod ID
curl https://19f2f827da7c-8000.proxy.runpod.net/health
```

Expected: `{"status":"healthy","message":"Backend is running",...}`

### 3.2 Test Backend API

**📱 MAC TERMINAL** - Check API status:
```bash
# Replace with your pod ID
curl https://19f2f827da7c-8000.proxy.runpod.net/api/status
```

Expected:
```json
{
  "backend": "running",
  "database_path": "/workspace/database.db",
  "projects_count": 1,
  "scans_count": 2,
  "projects": [...]
}
```

### 3.3 Test Frontend

**📱 MAC TERMINAL** - Open frontend:
```bash
open https://colmap-demo.vercel.app
```

Or manually visit: https://colmap-demo.vercel.app

### 3.4 Check Browser Console

In your browser:
1. Press `F12` or `Cmd+Option+I` to open Developer Tools
2. Go to **Console** tab
3. Refresh the page
4. Look for:
   - ✅ No CORS errors
   - ✅ No 502 errors
   - ✅ API requests succeeding

Expected console output:
```
🔍 Using Next.js API proxy: { url: '/api/backend', timestamp: '...' }
📊 Loaded 2 scans for project <project-id>
```

### 3.5 Test Dashboard

In the browser:
1. Navigate to **Dashboard**
2. Should see: "Reconstruction Test Project 1"
3. Click on the project
4. Should see demo scans:
   - demoscan-dollhouse
   - demoscan-fachada

### 3.6 Test 3D Viewer

In the browser:
1. Click on a demo scan (e.g., demoscan-dollhouse)
2. 3D viewer should load
3. Point cloud should display
4. No errors in console

---

## 🔧 Troubleshooting

### Problem: Backend Returns 502

**☁️ RUNPOD WEB TERMINAL** - Check if server is running:
```bash
ps aux | grep uvicorn
```

If not running, restart:
```bash
cd /workspace/colmap-demo
bash resume-runpod.sh
```

### Problem: Frontend Can't Connect

**📱 MAC TERMINAL** - Verify environment variable:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
cat .env.production
```

Should show: `NEXT_PUBLIC_API_URL="https://YOUR_POD_ID-8000.proxy.runpod.net"`

**📱 MAC TERMINAL** - Test backend directly:
```bash
curl https://YOUR_POD_ID-8000.proxy.runpod.net/health
```

If backend is fine but frontend still fails, redeploy:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
vercel --prod
```

### Problem: Database Empty

**☁️ RUNPOD WEB TERMINAL** - Reinitialize database:
```bash
cd /workspace/colmap-demo
source venv/bin/activate
python3 << 'EOF'
import asyncio
from database import Database

async def init_db():
    db = Database()
    await db.initialize()
    print('✅ Database initialized!')

asyncio.run(init_db())
EOF
```

Then restart backend:
```bash
bash resume-runpod.sh
```

### Problem: Pod ID Changed

If RunPod assigned a new pod ID:

**☁️ RUNPOD WEB TERMINAL** - Get current pod ID:
```bash
hostname
```

**📱 MAC TERMINAL** - Update .env.production:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
# Replace NEW_POD_ID with output from hostname command
echo 'NEXT_PUBLIC_API_URL="https://NEW_POD_ID-8000.proxy.runpod.net"' > .env.production
vercel --prod
```

### Problem: Backend Logs Show Errors

**☁️ RUNPOD WEB TERMINAL** - View full logs:
```bash
tail -n 100 /workspace/colmap-demo/backend.log
```

**☁️ RUNPOD WEB TERMINAL** - Follow logs in real-time:
```bash
tail -f /workspace/colmap-demo/backend.log
```

---

## 🛠️ Useful Commands

### Backend Management (RunPod)

**☁️ RUNPOD WEB TERMINAL** - Stop backend:
```bash
kill $(cat /workspace/colmap-demo/backend.pid)
```

**☁️ RUNPOD WEB TERMINAL** - Restart backend:
```bash
cd /workspace/colmap-demo
bash resume-runpod.sh
```

**☁️ RUNPOD WEB TERMINAL** - Check backend status:
```bash
ps aux | grep uvicorn
cat /workspace/colmap-demo/backend.pid
```

**☁️ RUNPOD WEB TERMINAL** - View backend logs:
```bash
tail -f /workspace/colmap-demo/backend.log
```

### Frontend Management (Mac)

**📱 MAC TERMINAL** - Build locally:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
npm run build
```

**📱 MAC TERMINAL** - Test locally:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
npm run dev
# Visit: http://localhost:3000
```

**📱 MAC TERMINAL** - Deploy to Vercel:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
vercel --prod
```

### Git Management (Mac)

**📱 MAC TERMINAL** - Pull latest changes:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
git pull origin main
```

**📱 MAC TERMINAL** - Check git status:
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
git status
```

---

## ✅ Success Checklist

- [ ] Backend responds: `curl https://POD_ID-8000.proxy.runpod.net/health`
- [ ] Frontend loads: https://colmap-demo.vercel.app
- [ ] Dashboard shows projects
- [ ] Demo scans visible
- [ ] 3D viewer works
- [ ] No console errors

---

## 📞 Support Resources

- **RunPod Dashboard:** https://www.runpod.io/console/pods
- **Vercel Dashboard:** https://vercel.com/interact-hq/colmap-demo
- **GitHub Repo:** https://github.com/marco-interact/colmap-demo

---

## 🎯 Quick Reference

| Task | Location | Command |
|------|----------|---------|
| Start backend | ☁️ RunPod | `bash resume-runpod.sh` |
| Stop backend | ☁️ RunPod | `kill $(cat backend.pid)` |
| View logs | ☁️ RunPod | `tail -f backend.log` |
| Deploy frontend | 📱 Mac | `bash deploy-frontend.sh` |
| Test backend | 📱 Mac | `curl https://POD_ID-8000.proxy.runpod.net/health` |
| Open frontend | 📱 Mac | `open https://colmap-demo.vercel.app` |

---

**Ready to deploy!** 🚀

