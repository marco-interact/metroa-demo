# ❌ Skip Docker - Use Direct Installation Instead

## 🚨 **Why Docker Doesn't Work on RunPod**

Your RunPod container is **already inside Docker**, and has these restrictions:

1. ❌ **No `overlay2` storage driver** - Permission denied
2. ❌ **No `iptables` access** - Networking blocked  
3. ❌ **Nested containers limited** - Resource conflicts

**Error you're seeing:**
```
iptables v1.8.10 (nf_tables): Could not fetch rule set generationid: 
Permission denied (you must be root)
```

---

## ✅ **THE SOLUTION: Direct Installation (2 Minutes)**

Skip Docker entirely! Install COLMAP directly on the RunPod container.

### **Benefits:**
- ✅ **2-3 minutes** (vs 5-45 min for Docker)
- ✅ **No permission issues**
- ✅ **Same features** (COLMAP, GPU, everything)
- ✅ **Simpler** - no Docker complexity

---

## 🚀 **Quick Start (Copy-Paste These 3 Commands)**

```bash
# 1. Pull latest code
cd /workspace/metroa-demo
git pull origin main

# 2. Install everything (2-3 minutes)
bash README/scripts/install-direct-runpod.sh

# 3. Start backend
bash README/scripts/start-backend-runpod.sh
```

**That's it!** Backend will be running at `http://localhost:8888`

---

## 📋 **What Gets Installed**

The install script (`install-direct-runpod.sh`) installs:

1. **COLMAP** - Pre-compiled from Ubuntu (GPU-enabled)
2. **FFmpeg** - Video processing
3. **Python packages** - FastAPI, Open3D, OpenCV, etc.
4. **System libraries** - OpenGL, graphics support
5. **Data directories** - uploads, results, cache

**Total time:** 2-3 minutes  
**Total space:** ~2 GB

---

## 🎯 **Step-by-Step Instructions**

### Step 1: Navigate and Pull

```bash
cd /workspace/metroa-demo
git pull origin main
```

**Expected output:**
```
Fast-forward
 5 files changed, 450 insertions(+)
 create mode 100755 README/scripts/install-direct-runpod.sh
 ...
```

### Step 2: Run Installation Script

```bash
bash README/scripts/install-direct-runpod.sh
```

**What happens:**
```
🚀 DIRECT INSTALLATION ON RUNPOD (NO DOCKER)
⏱️  Time: 2-3 minutes

📦 Step 1: Installing System Dependencies
✅ COLMAP installed: COLMAP 3.x

🐍 Step 2: Installing Python Dependencies
✅ FastAPI: 0.115.4
✅ Open3D: 0.19.0

📁 Step 3: Creating Data Directories
✅ Directories created

🧪 Step 4: Testing Backend Imports
✅ All backend imports successful

🎮 Step 5: Checking GPU
✅ GPU detected: NVIDIA GeForce RTX 4090, 24564 MiB

✅ INSTALLATION COMPLETE!
```

### Step 3: Start Backend

```bash
bash README/scripts/start-backend-runpod.sh
```

**What happens:**
```
🚀 STARTING METROA BACKEND

✅ Backend started in screen session 'metroa-backend'
⏳ Waiting for backend to start (10 seconds)...

✅ BACKEND IS RUNNING!

Health check response:
{
  "status": "healthy",
  "gpu_available": true,
  "message": "Server is running"
}
```

### Step 4: Verify It Works

```bash
curl http://localhost:8888/health
```

**Should return:**
```json
{"status":"healthy","gpu_available":true,"message":"Server is running"}
```

---

## 🔧 **Manual Start (If Needed)**

If the script doesn't work, start manually:

```bash
cd /workspace/metroa-demo

# Start in foreground (see output)
python main.py

# OR start in background (persistent)
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py"
```

---

## 📊 **Direct vs Docker Comparison**

| Method | Time | Complexity | Works on RunPod? |
|--------|------|------------|------------------|
| **Direct Install** ✅ | 2-3 min | Simple | YES |
| Docker (fast) | 5-10 min | Medium | NO (permissions) |
| Docker (full) | 30-45 min | Complex | NO (permissions) |

**Verdict:** Direct installation is best for RunPod!

---

## 🆘 **Troubleshooting**

### "colmap: command not found"

```bash
# Reinstall COLMAP
apt-get update && apt-get install -y colmap
colmap --version
```

### "ModuleNotFoundError"

```bash
# Reinstall Python packages
pip install -r requirements.txt
```

### Backend won't start

```bash
# Check for errors
python main.py
# (Watch the output for specific errors)

# Check if port is in use
lsof -i:8888
pkill -f "python.*main.py"
```

### View logs

```bash
# If started with script
tail -f logs/backend.log

# If in screen
screen -r metroa-backend
# Press Ctrl+A then D to detach
```

---

## 📋 **Useful Commands**

```bash
# Start backend
bash README/scripts/start-backend-runpod.sh

# Stop backend
pkill -f "python.*main.py"

# View logs
tail -f logs/backend.log

# Reconnect to screen session
screen -r metroa-backend

# Check backend status
curl http://localhost:8888/health

# Check if backend is running
ps aux | grep "python.*main.py"

# Check port 8888
lsof -i:8888
```

---

## ✅ **Success Checklist**

After installation:

- [ ] COLMAP installed: `colmap --version` works
- [ ] Python packages: `pip list | grep fastapi` shows packages
- [ ] Backend starts: `python main.py` runs without errors
- [ ] Health check OK: `curl http://localhost:8888/health` returns JSON
- [ ] GPU available: Response shows `"gpu_available": true`

---

## 🌐 **Access URLs**

After backend is running:

- **Local:** `http://localhost:8888`
- **Health:** `http://localhost:8888/health`
- **API Docs:** `http://localhost:8888/docs`
- **RunPod Proxy:** `https://YOUR-POD-ID-8888.proxy.runpod.net`

Find your Pod ID:
```bash
echo $(hostname)-8888.proxy.runpod.net
```

---

## 📞 **Next Steps**

1. ✅ Backend running on RunPod (direct install)
2. Deploy frontend on Vercel:
   ```bash
   # On your Mac
   cd /Users/marco.aurelio/Desktop/metroa-demo
   vercel --prod
   ```

3. Update frontend to use RunPod backend URL in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` = `https://YOUR-POD-ID-8888.proxy.runpod.net`

---

## 🎉 **Why This Is Better**

1. **Faster:** 2-3 minutes vs 5-45 minutes
2. **Simpler:** No Docker complexity
3. **Works:** No permission issues
4. **Same features:** COLMAP GPU, all processing
5. **Easier debugging:** Direct access to logs and processes

---

## 🔑 **Key Takeaway**

**RunPod IS Docker** - you don't need Docker-in-Docker.  
Just install directly on the container!

---

**Your 3 commands:**

```bash
cd /workspace/metroa-demo && \
git pull origin main && \
bash README/scripts/install-direct-runpod.sh && \
bash README/scripts/start-backend-runpod.sh
```

**Done in 2-3 minutes!** 🚀


