# RunPod Setup Command

## Quick Setup (One-Liner)

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull origin main) && cd metroa-demo && chmod +x setup-metroa-pod.sh && bash setup-metroa-pod.sh
```

---

## Step-by-Step Commands

### Option 1: Fresh Setup (New Pod)

```bash
# Navigate to workspace
cd /workspace

# Clone repository (if not exists)
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# Make script executable
chmod +x setup-metroa-pod.sh

# Run setup script
bash setup-metroa-pod.sh
```

### Option 2: Update Existing Setup

```bash
# Navigate to repository
cd /workspace/metroa-demo

# Pull latest changes
git pull origin main

# Run setup script (will rebuild if needed)
bash setup-metroa-pod.sh
```

### Option 3: Force Clean Rebuild

```bash
# Navigate to workspace
cd /workspace

# Remove existing setup
rm -rf metroa-demo

# Clone fresh
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# Run setup
bash setup-metroa-pod.sh
```

---

## What the Script Does

The setup script (`setup-metroa-pod.sh`) performs 9 steps:

1. ✅ **System Dependencies** - Installs all required packages
2. ✅ **COLMAP Build** - Builds COLMAP 3.10 with GPU support (RTX 4090)
3. ✅ **OpenMVS Build** - Builds OpenMVS v2.2.0 for ultra quality mode
4. ✅ **Clone Repository** - Clones/updates metroa-demo repository
5. ✅ **Python Environment** - Sets up venv and installs dependencies
6. ✅ **Persistent Storage** - Configures volume mounts
7. ✅ **Database** - Initializes SQLite with demo data
8. ✅ **Verification** - Tests COLMAP GPU and OpenMVS
9. ✅ **Backend Server** - Starts FastAPI on port 8888

**Total Time:** ~30-40 minutes (most time spent building COLMAP + OpenMVS)

---

## Expected Output

```
==================================================
🚀 METROA POD - Complete Setup
==================================================

==> Step 1/9: Installing system dependencies...
✅ System dependencies installed

==> Step 2/9: Building COLMAP with GPU support...
✅ COLMAP installed with GPU support

==> Step 3/9: Building OpenMVS for ultra quality mode...
✅ OpenMVS installed successfully

==> Step 4/9: Cloning metroa-demo repository...
✅ Repository cloned

==> Step 5/9: Setting up Python environment...
✅ Python dependencies installed

==> Step 6/9: Configuring persistent storage...
✅ Persistent storage configured

==> Step 7/9: Initializing database...
✅ Database initialized with demo data

==> Step 8/9: Testing COLMAP GPU and OpenMVS functionality...
✅ GPU feature extraction works!
✅ OpenMVS tools available!

==> Step 9/9: Starting backend server...
✅ Backend server started!

==================================================
✨ METROA POD SETUP COMPLETE!
==================================================
```

---

## Troubleshooting

### If script fails mid-way:

```bash
# Check logs
tail -f /workspace/metroa-demo/backend.log

# Check if backend is running
curl http://localhost:8888/health

# Restart from beginning
cd /workspace/metroa-demo
bash setup-metroa-pod.sh
```

### If OpenMVS build fails:

```bash
# Check OpenMVS build directory
ls -la /workspace/openMVS/build

# Manually verify dependencies
apt-get install -y libcgal-dev libcgal-qt5-dev libgl1-mesa-dev libglu1-mesa-dev

# Retry OpenMVS build
cd /workspace/openMVS/build
make -j8
make install
```

### If backend doesn't start:

```bash
# Check port 8888
lsof -i :8888

# Kill existing process
lsof -ti:8888 | xargs kill -9 2>/dev/null || true

# Start manually
cd /workspace/metroa-demo
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888
```

---

## Verification Commands

After setup completes, verify everything works:

```bash
# Check COLMAP
colmap -h | head -1

# Check OpenMVS
DensifyPointCloud --help | head -1
InterfaceCOLMAP --help | head -1

# Check Python packages
source /workspace/metroa-demo/venv/bin/activate
python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python3 -c "import open3d as o3d; print(f'Open3D {o3d.__version__}')"

# Check backend
curl http://localhost:8888/health
curl http://localhost:8888/api/status
```

---

## Backend URL

After setup, your backend will be available at:

```
https://<POD_ID>-8888.proxy.runpod.net
```

Replace `<POD_ID>` with your actual RunPod pod ID (shown in the setup output).

