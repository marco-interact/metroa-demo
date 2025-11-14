# 🚀 Setup Backend on New Pod 8pexe48luksdw3

**Complete automated setup - just run one command**

---

## ⚡ Quick Setup (One Command)

**On RunPod Web Terminal or SSH, run:**

```bash
cd /workspace && rm -rf metroa-demo && git clone https://github.com/marco-interact/metroa-demo.git && cd metroa-demo && chmod +x setup-pod-8pexe48luksdw3.sh && bash setup-pod-8pexe48luksdw3.sh
```

**⏱️ Time:** 15-20 minutes (COLMAP build takes ~10-15 min)

---

## 📋 What This Does

1. ✅ Installs all system dependencies (git, cmake, ninja, ffmpeg, etc.)
2. ✅ Builds COLMAP with RTX 4090 GPU support (CUDA 12, compute capability 8.9)
3. ✅ Clones metroa-demo repository
4. ✅ Sets up Python virtual environment
5. ✅ Installs all Python dependencies (FastAPI, Open3D, etc.)
6. ✅ Configures persistent storage
7. ✅ Initializes database with demo data
8. ✅ Tests COLMAP GPU functionality
9. ✅ Starts backend server on port 8888

---

## 🔍 Verify Setup

After the script completes, verify:

```bash
# Check backend is running
curl http://localhost:8888/health

# Should return:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}

# Check logs
tail -20 /workspace/metroa-demo/backend.log

# Check process
ps aux | grep uvicorn | grep -v grep
```

---

## 🌐 Test Public URL

**From your Mac:**

```bash
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health
```

Should return the same health check response.

---

## 🔧 If Setup Fails

### Check Logs

```bash
tail -50 /workspace/metroa-demo/backend.log
```

### Manual Restart

```bash
cd /workspace/metroa-demo
source venv/bin/activate
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
export QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
sleep 5
curl http://localhost:8888/health
```

---

## 📋 Pod Details

- **Pod ID:** `8pexe48luksdw3`
- **Name:** `metroa_worker_gpu`
- **GPU:** RTX 4090 (24GB VRAM)
- **Port:** 8888
- **Public URL:** `https://8pexe48luksdw3-8888.proxy.runpod.net`
- **Volume:** `metroa-volume` (mvmh2mg1pt)

---

## ✅ Next Steps

After backend is running:

1. **Update Frontend:**
   ```bash
   cd /Users/marco.aurelio/Desktop/metroa-demo
   echo 'NEXT_PUBLIC_API_URL="https://8pexe48luksdw3-8888.proxy.runpod.net"' > .env.production
   vercel --prod
   ```

2. **Verify Everything:**
   - Backend health check: ✅
   - Frontend connects: ✅
   - 3D viewer loads: ✅

---

**Ready!** Your backend is now set up on the new pod. 🚀

