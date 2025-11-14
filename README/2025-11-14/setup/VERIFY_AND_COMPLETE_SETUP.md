# ✅ Verify and Complete Full Setup

**After cloning the repo, you MUST run the setup script to install everything**

---

## 🔍 Step 1: Check Current Status

**On RunPod terminal, run:**

```bash
cd /workspace/metroa-demo

# Check if setup script exists
ls -la setup-pod-8pexe48luksdw3.sh

# Check what's installed
which colmap
python3 --version
pip --version
```

---

## 🚀 Step 2: Run FULL Setup Script

**This installs EVERYTHING:**

```bash
cd /workspace/metroa-demo
bash setup-pod-8pexe48luksdw3.sh
```

**This will:**
1. ✅ Install ALL system dependencies (git, cmake, ffmpeg, etc.)
2. ✅ Build COLMAP with GPU support (~10-15 min)
3. ✅ Setup Python virtual environment
4. ✅ Install ALL Python dependencies (FastAPI, Open3D, etc.)
5. ✅ Configure persistent storage
6. ✅ Initialize database with demo data
7. ✅ Start backend server on port 8888

**⏱️ Total time: 15-20 minutes**

---

## 📋 What Gets Installed

### System Dependencies:
- git, wget, curl
- build-essential, cmake, ninja-build
- libboost-all-dev, libeigen3-dev
- libflann-dev, libfreeimage-dev
- libmetis-dev, libgoogle-glog-dev
- libgflags-dev, libsqlite3-dev
- libglew-dev, libcgal-dev, libceres-dev
- libegl1-mesa-dev, libgles2-mesa-dev
- python3-pip, sqlite3, unzip, ffmpeg, lsof

### COLMAP:
- Built from source with RTX 4090 GPU support
- CUDA 12.8 optimized
- Compute capability 8.9

### Python Dependencies (from requirements.txt):
- fastapi==0.115.4
- uvicorn[standard]==0.32.0
- python-multipart==0.0.12
- opencv-python==4.10.0.84
- numpy==1.26.4
- open3d==0.19.0
- aiosqlite==0.20.0
- python-dotenv==1.0.1
- pydantic==2.9.2
- pydantic-settings==2.6.0

---

## ✅ Step 3: Verify Installation

**After setup completes, verify:**

```bash
# Check COLMAP
colmap -h | head -1

# Check Python
python3 --version

# Check virtual environment
source /workspace/metroa-demo/venv/bin/activate
pip list | grep -E "fastapi|open3d|opencv"

# Check backend
curl http://localhost:8888/health

# Check GPU
nvidia-smi
```

---

## 🔧 If Setup Script Fails

**Check logs:**
```bash
cd /workspace/metroa-demo
tail -f backend.log
```

**Manual dependency check:**
```bash
# System dependencies
apt-get update
apt-get install -y git python3-pip ffmpeg sqlite3 build-essential cmake ninja-build

# Python dependencies
cd /workspace/metroa-demo
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚠️ Important

**Just cloning the repo is NOT enough!** You MUST run:
```bash
bash setup-pod-8pexe48luksdw3.sh
```

This script does EVERYTHING - don't skip it!

