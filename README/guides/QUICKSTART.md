# 🚀 Metroa Labs - Production Deployment Quickstart

## ✅ Current Status

**Repository**: https://github.com/marco-interact/metroa-demo  
**Status**: ✅ All MVP features implemented and production-ready

**Demo Credentials:**
- Email: `demo@metroa.app`
- Password: `demo123`

---

## 🎯 Quick Deploy (2 Steps)

### Step 1: Setup RunPod Backend (15-20 minutes)

**Connect to RunPod Pod:**
```bash
# SSH into pod (update with your pod details)
ssh root@<POD_IP> -p <PORT> -i ~/.ssh/id_ed25519

# Or use RunPod Web Terminal
```

**Run Setup Script:**
```bash
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo
bash setup-metroa-pod.sh
```

**What This Does:**
1. ✅ Installs system dependencies (FFmpeg, CUDA, etc.)
2. ✅ Builds COLMAP 3.10 with RTX 4090 GPU support
3. ✅ Sets up Python 3.12 environment
4. ✅ Installs Python dependencies (FastAPI, OpenCV, Open3D, etc.)
5. ✅ Configures persistent storage (`/workspace/data`)
6. ✅ Initializes SQLite database with demo data
7. ✅ Starts FastAPI backend on port 8888

**Expected Output:**
```
✨ METROA POD SETUP COMPLETE!
Backend running on: http://0.0.0.0:8888
✅ READY FOR PRODUCTION!
```

**Backend URL Format:**
```
https://<POD_ID>-8888.proxy.runpod.net
```

---

### Step 2: Deploy Frontend to Vercel (2 minutes)

**On Your Local Machine:**
```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Set backend URL (replace with your RunPod pod URL)
echo 'NEXT_PUBLIC_API_URL="https://<POD_ID>-8888.proxy.runpod.net"' > .env.production

# Deploy to Vercel
vercel --prod
```

**When Prompted:**
- Scope: `interact-hq`
- Link to existing: `No` (or `Yes` if updating)
- Project name: `metroa-demo`
- Directory: `./`
- Override settings: `No`

---

## ✅ Verify Deployment

**Test Backend:**
```bash
curl https://<POD_ID>-8888.proxy.runpod.net/health
# Should return: {"status":"healthy",...}
```

**Test Frontend:**
- Open: `https://metroa-demo.vercel.app`
- Login with: `demo@metroa.app` / `demo123`
- Verify:
  - ✅ Dashboard loads with demo project
  - ✅ 3D viewer displays point clouds
  - ✅ Measurement tool works (point selection)
  - ✅ Video upload works

---

## 🎨 Current Features

### ✅ All MVP Features Implemented

1. **360° Video Upload Interface**
   - Automatic detection of equirectangular videos
   - Multi-view perspective conversion (8 views per frame)
   - Integrated into upload pipeline

2. **Interactive 3D Visualization**
   - Three.js + React Three Fiber
   - PLY point cloud loading and rendering
   - Orbit controls, camera controls, fullscreen
   - Point selection with visual indicators

3. **Measurement Tool**
   - Point selection (Point A = Green 🟢, Point B = Blue 🔵)
   - Scale calibration with known distance
   - Distance measurement and export (JSON/CSV)
   - Image capture from 3D viewer

4. **Video Processing Pipeline**
   - Frame extraction (FFmpeg with auto FPS detection)
   - Perspective image conversion (OpenCV for 360° videos)
   - Automatic 3D reconstruction (COLMAP)
   - Model export (PLY/GLTF/GLB)

5. **Quality Presets**
   - **Fast**: 30-60s, 50K-200K points
   - **High Quality**: 3-5 min, 1M-5M points (default)
   - **Ultra (OpenMVS)**: 5-10 min, 5M-20M points

6. **Processing Status Monitoring**
   - Real-time progress bars
   - Stage-by-stage tracking
   - Detailed progress updates

---

## 📦 Technology Stack

### Backend
- **Python 3.12** + FastAPI
- **COLMAP 3.10** (GPU-accelerated)
- **OpenMVS** (ultra quality densification)
- **Open3D** (point cloud post-processing)
- **OpenCV** (360° video conversion)
- **FFmpeg** (frame extraction)
- **SQLite** (database)

### Frontend
- **Next.js 14** (React framework)
- **Three.js** + React Three Fiber (3D rendering)
- **TypeScript** (type safety)
- **Tailwind CSS** (styling)
- **Shadcn UI** (components)

---

## 🔧 Quick Commands

### Backend (RunPod)
```bash
# Check status
curl http://localhost:8888/health

# View logs
tail -f /workspace/metroa-demo/backend.log

# Restart backend
pkill -f "python.*main.py"
cd /workspace/metroa-demo
source venv/bin/activate
python main.py > backend.log 2>&1 &
```

### Frontend (Local)
```bash
# Test locally
npm run dev

# Deploy to Vercel
vercel --prod

# Update backend URL
echo 'NEXT_PUBLIC_API_URL="https://<POD_ID>-8888.proxy.runpod.net"' > .env.production
```

---

## 📊 Performance Targets

| Quality | Video Length | Processing Time | Point Cloud Size |
|---------|--------------|-----------------|------------------|
| Fast | 10-20s | 30-60s | 50K-200K points |
| High | 10-20s | 3-5 min | 1M-5M points |
| Ultra | 10-20s | 5-10 min | 5M-20M points |

---

## 📁 Project Structure

```
metroa-demo/
├── main.py                    # FastAPI backend
├── colmap_processor.py         # COLMAP pipeline
├── quality_presets.py          # Quality presets (fast/high/ultra)
├── video_360_converter.py     # 360° video support
├── ply_to_gltf.py             # GLTF export
├── pointcloud_postprocess.py  # Open3D post-processing
├── openmvs_processor.py       # OpenMVS integration
├── database.py                # SQLite database
├── setup-metroa-pod.sh        # Master setup script
├── build-colmap-gpu-fixed.sh  # COLMAP GPU build
│
├── src/                       # Next.js frontend
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   │   ├── 3d/               # Three.js viewers
│   │   └── ui/               # UI components
│   └── lib/                   # API client
│
├── README/                    # Documentation (organized by date)
│   └── YYYY-MM-DD/           # Date-based folders
│       ├── troubleshooting/  # Debug guides
│       ├── setup/            # Setup guides
│       └── deployment/       # Deployment docs
│
└── demo-resources/            # Demo 3D models
```

---

## 🎉 Ready to Deploy!

**Next Steps:**
1. Run Step 1 (RunPod setup)
2. Run Step 2 (Vercel deployment)
3. Verify deployment
4. Start uploading videos! 🚀

**All MVP features are implemented and ready for production use.**
