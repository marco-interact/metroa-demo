# ✅ Next Steps After Pod Setup

**After running `setup-pod-8pexe48luksdw3.sh`, follow these steps:**

---

## Step 1: Verify Backend is Running

**On RunPod (in the web terminal):**

```bash
# Check if backend is running
curl http://localhost:8888/health

# Should return: {"status":"healthy",...}

# Check backend logs
tail -f /workspace/metroa-demo/backend.log

# Check backend process
ps aux | grep uvicorn
```

**From Your Mac:**

```bash
# Test public URL
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health

# Should return: {"status":"healthy",...}
```

---

## Step 2: Update Frontend Backend URL

**On Your Mac Terminal:**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Option A: Use automated script
bash update-frontend-pod-8pexe48luksdw3.sh

# Option B: Manual update
echo 'NEXT_PUBLIC_API_URL="https://8pexe48luksdw3-8888.proxy.runpod.net"' > .env.production
npm run build
vercel --prod
```

---

## Step 3: Verify Everything Works

**Test Backend:**
```bash
# Health check
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health

# API status
curl https://8pexe48luksdw3-8888.proxy.runpod.net/api/status

# Should show: {"projects_count": 1, "scans_count": 1}
```

**Test Frontend:**
1. Open: https://metroa-demo.vercel.app
2. Should see:
   - ✅ Dashboard loads
   - ✅ "Reconstruction Test Project 1" visible
   - ✅ "Dollhouse Scan" visible
   - ✅ Can click into scan
   - ✅ 3D viewer loads point cloud
   - ✅ Measurement tool works

---

## Step 4: Test a Video Upload (Optional)

1. Go to project page
2. Click "New Scan"
3. Upload a small test video (10-20 seconds)
4. Select quality mode (Fast/High Quality/Ultra)
5. Watch processing progress
6. Verify point cloud appears when complete

---

## 🔧 Troubleshooting

### Backend Not Responding?

**On RunPod:**
```bash
cd /workspace/metroa-demo
tail -f backend.log

# If not running, restart:
kill $(cat backend.pid) 2>/dev/null || true
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

### Frontend Can't Connect?

1. Verify backend URL in `.env.production`:
   ```bash
   cat .env.production
   # Should show: NEXT_PUBLIC_API_URL="https://8pexe48luksdw3-8888.proxy.runpod.net"
   ```

2. Verify backend is accessible:
   ```bash
   curl https://8pexe48luksdw3-8888.proxy.runpod.net/health
   ```

3. Redeploy frontend:
   ```bash
   vercel --prod
   ```

### Database Not Found?

**On RunPod:**
```bash
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "from database import db; db.setup_demo_data()"
```

---

## 📋 Quick Checklist

- [ ] Backend health check returns `200 OK`
- [ ] Backend API status shows demo data
- [ ] Frontend `.env.production` updated
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads dashboard
- [ ] Demo scan visible and clickable
- [ ] 3D viewer loads point cloud
- [ ] Measurement tool works

---

## 🎉 You're Done!

Once all checks pass, your new pod is fully operational and ready for video uploads!

**Backend URL:** `https://8pexe48luksdw3-8888.proxy.runpod.net`  
**Frontend URL:** `https://metroa-demo.vercel.app`

