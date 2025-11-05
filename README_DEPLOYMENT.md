# 🚀 Resume CI/CD Deployment - Quick Start

**Last Updated:** November 5, 2025  
**Status:** Backend offline, ready to resume

---

## 🎯 Quick Fix (5 minutes)

### Problem
Frontend can't connect to backend → **502 Bad Gateway**

### Solution
Backend not running on RunPod. Follow these 2 steps:

---

## Step 1: Start Backend (RunPod)

**SSH into your RunPod pod:**
```bash
# Get SSH command from: https://www.runpod.io/console/pods
# Look for pod: xhqt6a1roo8mrc (colmap_worker_gpu)
```

**Run the startup script:**
```bash
cd /workspace/colmap-demo
bash resume-runpod.sh
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

---

## Step 2: Deploy Frontend (Local)

**On your local machine:**
```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
bash deploy-frontend.sh
```

This will:
- ✅ Test backend connection
- ✅ Build Next.js app
- ✅ Deploy to Vercel

---

## ✅ Verify Success

**Backend health check:**
```bash
curl https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health
# Expected: {"status":"healthy",...}
```

**Frontend:**
- Visit: https://colmap-demo.vercel.app
- Should see demo projects loaded
- No errors in browser console

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **DEPLOYMENT_QUICKSTART.md** | Quick commands and troubleshooting |
| **DEPLOYMENT_CHECKLIST.md** | Detailed step-by-step checklist |
| **CICD_RESUME_GUIDE.md** | Comprehensive deployment guide |
| **cursor-logs/2025-11-05/** | Technical session summary |

---

## 🆘 Troubleshooting

### Backend returns 502
→ Run `resume-runpod.sh` on RunPod

### Frontend can't connect
→ Check `.env.production` and redeploy

### Database empty
→ Backend startup script reinitializes it automatically

---

## 📞 Support

- **RunPod Dashboard:** https://www.runpod.io/console/pods
- **Vercel Dashboard:** https://vercel.com/interact-hq/colmap-demo
- **Full Guide:** Read `CICD_RESUME_GUIDE.md`

---

**Ready to deploy!** 🎉

