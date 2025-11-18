# 🚀 RunPod Complete Setup Guide

## ⚠️ THE PROBLEM

You're experiencing crashes because:
1. **COLMAP is NOT installed natively on RunPod** - it only exists in the Docker image
2. **Running `python main.py` directly fails** - Python can't find COLMAP
3. **The Dockerfile builds COLMAP from source** - takes 30-45 minutes each time

## ✅ THE SOLUTION: Use Pre-Built Docker Container

You have **3 options**:

---

## 🎯 Option 1: Quick Install COLMAP (Fastest - 2 minutes)

Install COLMAP directly on the RunPod pod:

```bash
# SSH into RunPod, then:
cd /workspace/metroa-demo

# Install COLMAP from Ubuntu repositories (pre-compiled)
apt-get update && apt-get install -y colmap ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{uploads,results,cache}

# Start backend (no Docker needed)
python main.py
```

**Pros:** ✅ Fast (2 minutes), ✅ Simple  
**Cons:** ⚠️ May not have GPU acceleration (depends on Ubuntu package)

---

## 🐳 Option 2: Use Docker Container (Recommended for Production)

Build and run the Docker container with COLMAP pre-built:

```bash
# SSH into RunPod, then:
cd /workspace/metroa-demo

# Start Docker daemon (if not running)
dockerd > /dev/null 2>&1 &
sleep 3

# Build Docker image (30-45 minutes first time, cached after)
docker build -t metroa-backend .

# Run container with GPU
docker run -d \
  --name metroa-backend \
  --gpus all \
  -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend

# Wait for startup
sleep 10

# Test
curl http://localhost:8888/health
```

**Pros:** ✅ GPU-accelerated COLMAP, ✅ Isolated environment, ✅ Production-ready  
**Cons:** ⏳ Long initial build time (30-45 min)

---

## 🏗️ Option 3: Build COLMAP with GPU (Advanced - 30 minutes)

Build COLMAP from source with GPU support on the pod:

```bash
# SSH into RunPod, then:
cd /workspace/metroa-demo

# Run the build script
bash README/scripts/build-colmap-gpu-fixed.sh

# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/{uploads,results,cache}

# Start backend
python main.py
```

**Pros:** ✅ GPU-accelerated, ✅ No Docker overhead  
**Cons:** ⏳ Slow initial setup (30 min)

---

## 🎬 RECOMMENDED WORKFLOW: One-Time Docker Build

The best approach is to **build Docker once, push to Docker Hub, then pull on RunPod**:

### Step 1: Build on RunPod (One Time)

```bash
cd /workspace/metroa-demo

# Start Docker
dockerd > /dev/null 2>&1 &
sleep 3

# Build image (30-45 min)
docker build -t metroa-backend:latest .

# Test it works
docker run -d --name test --gpus all -p 8888:8888 metroa-backend:latest
sleep 10
curl http://localhost:8888/health

# If working, tag and push (optional - requires Docker Hub account)
# docker tag metroa-backend:latest yourusername/metroa-backend:latest
# docker push yourusername/metroa-backend:latest
```

### Step 2: Future Deployments (Fast)

```bash
# Just pull and run (no rebuild needed)
docker pull yourusername/metroa-backend:latest
docker run -d --name metroa-backend --gpus all -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  yourusername/metroa-backend:latest
```

---

## 🚀 QUICK START: Install COLMAP Now (Do This First!)

**Run this on RunPod RIGHT NOW:**

```bash
cd /workspace/metroa-demo

# Quick install
apt-get update && apt-get install -y colmap ffmpeg libgl1-mesa-glx libglib2.0-0

# Install Python deps
pip install -r requirements.txt

# Create dirs
mkdir -p data/{uploads,results,cache}

# Test COLMAP
colmap --version

# Start backend
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py"

# Test
sleep 5
curl http://localhost:8888/health
```

**This takes 2 minutes and gets you running immediately!**

---

## 🔍 Verify Installation

After setup, verify everything works:

```bash
# 1. Check COLMAP
colmap --version
# Should show: COLMAP 3.x

# 2. Check Python packages
python -c "import fastapi, cv2, numpy, open3d; print('✅ All packages OK')"

# 3. Check CUDA/GPU
nvidia-smi

# 4. Test imports
python -c "from colmap_processor import COLMAPProcessor; print('✅ Backend can import COLMAP processor')"

# 5. Start backend
python main.py
# Should show: "Uvicorn running on http://0.0.0.0:8888"
```

---

## 📊 Comparison Table

| Method | Setup Time | GPU Support | Complexity | Best For |
|--------|-----------|-------------|-----------|----------|
| **apt install** | 2 min | Maybe | Low | Quick testing |
| **Docker** | 45 min (once) | ✅ Yes | Medium | Production |
| **Build from source** | 30 min | ✅ Yes | High | Custom builds |

---

## 🆘 Troubleshooting

### "colmap: command not found"

```bash
# Install COLMAP
apt-get update && apt-get install -y colmap

# Or use Docker
docker run -d --gpus all -p 8888:8888 metroa-backend
```

### "ModuleNotFoundError: No module named 'fastapi'"

```bash
pip install -r requirements.txt
```

### "Docker daemon not running"

```bash
# Start Docker
dockerd > /dev/null 2>&1 &
sleep 3

# Verify
docker ps
```

### Backend crashes immediately

```bash
# Run diagnostic
cd /workspace/metroa-demo
bash README/scripts/diagnose-crash.sh
```

---

## 🎯 My Recommendation

**For immediate testing:**
```bash
apt-get update && apt-get install -y colmap ffmpeg
pip install -r requirements.txt
mkdir -p data/{uploads,results,cache}
python main.py
```

**For production (do this next):**
```bash
docker build -t metroa-backend .
docker run -d --gpus all -p 8888:8888 -v /workspace/metroa-demo/data:/workspace/data metroa-backend
```

---

## ✅ Success Checklist

- [ ] COLMAP installed: `colmap --version` works
- [ ] Python deps installed: `pip list | grep fastapi` shows packages
- [ ] Directories created: `ls -la data/` shows uploads/results/cache
- [ ] Backend starts: `python main.py` shows "Uvicorn running"
- [ ] Health check works: `curl http://localhost:8888/health` returns JSON
- [ ] GPU available: `nvidia-smi` shows GPU info

---

**Next:** Once working, run `cat README/troubleshooting/DIAGNOSE_BACKEND_CRASH.md` for advanced debugging.


