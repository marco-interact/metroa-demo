# ⚡ Quick Deployment Commands

## 🔧 Backend (RunPod)

```bash
# SSH into RunPod
ssh root@203.57.40.132 -p 10164

# Pull & restart backend
cd /workspace/metroa-demo && \
git pull metroa main && \
kill $(cat backend.pid 2>/dev/null) || pkill -f uvicorn && \
source venv/bin/activate && \
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 & \
echo $! > backend.pid && \
sleep 3 && \
curl http://localhost:8888/health

# Check logs
tail -f backend.log
```

---

## 🌐 Frontend (Vercel)

```bash
# From your Mac
cd /Users/marco.aurelio/Desktop/metroa-demo

# Deploy to production
npx vercel --prod
```

---

## 🧪 Test in Browser

1. Open your Vercel URL
2. Upload a video (40 seconds recommended)
3. Select **High Quality** mode
4. Wait 3-5 minutes
5. View dense point cloud + mesh!

---

## 📊 Monitor Progress

```bash
# SSH into RunPod
ssh root@203.57.40.132 -p 10164

# Watch logs
tail -f /workspace/metroa-demo/backend.log | grep -E "mesh|Mesh|🔨|✅|progress"
```

---

## ✅ Verify Success

Look for these in logs:
- `✅ Registered X/Y images (XX% coverage)`
- `✅ Dense reconstruction: X,XXX,XXX points`
- `🔨 Generating mesh from point cloud`
- `✅ Mesh generated: XXX,XXX vertices, XXX,XXX triangles`

---

## 🎯 That's It!

**Backend**: Updated ✅  
**Frontend**: Deployed ✅  
**Ready to Test**: Through web app ✅

