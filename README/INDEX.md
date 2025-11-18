# 📚 Metroa Documentation Index

## 🚀 Quick Start

**New to Metroa?** Start here:

1. **[Main README](../README.md)** - Project overview and quick start
2. **[RunPod Docker Guide](../RUNPOD_DOCKER_GUIDE.md)** - Deploy backend (COMPLETE GUIDE)
3. **[Docker Quickstart](../DOCKER_QUICKSTART.md)** - Quick reference for Docker
4. **[Vercel Deploy](deployment/VERCEL_DEPLOY.md)** - Deploy frontend

---

## 📦 Backend Deployment

### **Recommended Workflow:**

```bash
# 1. Build Docker image locally (on your Mac)
bash docker-build-local.sh

# 2. Push to Docker Hub
docker login
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest

# 3. Deploy on RunPod
# Use YOUR_USERNAME/metroa-backend:latest in RunPod template
# GPU: RTX 4090, Port: 8888
```

**Full guide:** [RUNPOD_DOCKER_GUIDE.md](../RUNPOD_DOCKER_GUIDE.md)

---

## 🎨 Frontend Deployment

```bash
# Deploy to Vercel
vercel --prod
```

**Full guide:** [deployment/VERCEL_DEPLOY.md](deployment/VERCEL_DEPLOY.md)

---

## 📖 Technical Guides

### Architecture & Processing
- **[Stack and Architecture](guides/STACK_AND_ARCHITECTURE.md)** - System overview
- **[Processing Workflow](guides/PROCESSING_WORKFLOW.md)** - How 3D reconstruction works
- **[Reconstruction Optimization](guides/RECONSTRUCTION_OPTIMIZATION_GUIDE.md)** - COLMAP tuning

### Features
- **[Mesh Generation](guides/MESH_GENERATION_GUIDE.md)** - Creating 3D meshes
- **[Ultra Dense Optimization](guides/ULTRA_DENSE_OPTIMIZATION.md)** - High-quality point clouds
- **[Mobile Optimization](guides/MOBILE_OPTIMIZATION.md)** - Mobile performance

### Viewers & UI
- **[First Person Viewer](guides/FIRST_PERSON_VIEWER_GUIDE.md)** - FPS navigation
- **[FPS Viewer Advanced](guides/FPS_VIEWER_ADVANCED.md)** - Advanced features
- **[FPS Viewer Summary](guides/FPS_VIEWER_SUMMARY.md)** - Overview

### Integrations
- **[FFmpeg Integration](guides/FFMPEG_INTEGRATION.md)** - Video processing
- **[OpenCV FFmpeg](guides/OPENCV_FFMPEG_INTEGRATION.md)** - OpenCV + FFmpeg
- **[OpenCV SFM](guides/OPENCV_SFM_INTEGRATION.md)** - Structure from Motion
- **[Point Cloud Distance](guides/POINTCLOUD_DISTANCE_USAGE.md)** - Measurements
- **[Open3D Analysis](guides/OPEN3D_ANALYSIS.md)** - 3D processing library

### Measurements
- **[Measurement Implementation](guides/MEASUREMENT_IMPLEMENTATION_SUMMARY.md)** - How measurements work
- **[Measurement System Analysis](guides/MEASUREMENT_SYSTEM_ANALYSIS.md)** - Technical details

---

## 🗂️ Directory Structure

```
metroa-demo/
├── README.md                     # Main documentation
├── RUNPOD_DOCKER_GUIDE.md        # ⭐ Main deployment guide
├── DOCKER_QUICKSTART.md          # Quick Docker reference
├── docker-build-local.sh         # ⭐ Build script
├── Dockerfile                    # Production build (30-45 min)
├── Dockerfile.fast               # ⭐ Fast build (5-10 min)
├── requirements.txt              # Python dependencies
│
├── src/                          # Frontend (Next.js)
│   ├── app/                      # App routes
│   ├── components/               # React components
│   └── lib/                      # Utilities
│
├── *.py                          # Backend (FastAPI)
│   ├── main.py                   # API server
│   ├── colmap_processor.py       # COLMAP processing
│   ├── mesh_generator.py         # Mesh generation
│   └── database.py               # SQLite database
│
└── README/                       # Additional documentation
    ├── deployment/               # Deployment guides
    │   └── VERCEL_DEPLOY.md      # Frontend deployment
    └── guides/                   # Technical guides
```

---

## 🔑 Key Files

### **Essential:**
- `docker-build-local.sh` - Build Docker image locally
- `RUNPOD_DOCKER_GUIDE.md` - Complete deployment guide
- `Dockerfile.fast` - Fast Docker build (recommended)
- `requirements.txt` - Python dependencies
- `main.py` - FastAPI backend server

### **Configuration:**
- `.env` - Environment variables (create from `.env.example`)
- `vercel.json` - Vercel deployment config
- `next.config.js` - Next.js configuration

---

## 🎯 Common Tasks

### Build Docker Image:
```bash
bash docker-build-local.sh
# Select option 1 (Fast Build)
```

### Push to Docker Hub:
```bash
docker login
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest
```

### Deploy Backend:
- See [RUNPOD_DOCKER_GUIDE.md](../RUNPOD_DOCKER_GUIDE.md)

### Deploy Frontend:
```bash
vercel --prod
```

### Test Backend Locally:
```bash
docker run -d -p 8888:8888 metroa-backend:fast
curl http://localhost:8888/health
```

---

## 💡 Tips

1. **Always use `Dockerfile.fast`** - Much faster, same features
2. **Build locally, not on RunPod** - More reliable, easier debugging
3. **Use Docker Hub** - Central registry for images
4. **No persistent storage needed** - Everything is in the Docker image
5. **Update workflow:** Rebuild → Push → Restart RunPod pod

---

## 🆘 Need Help?

1. **Start with:** [RUNPOD_DOCKER_GUIDE.md](../RUNPOD_DOCKER_GUIDE.md)
2. **Quick reference:** [DOCKER_QUICKSTART.md](../DOCKER_QUICKSTART.md)
3. **Frontend deployment:** [deployment/VERCEL_DEPLOY.md](deployment/VERCEL_DEPLOY.md)

---

**Last Updated:** November 18, 2024
**Documentation Version:** 2.0 (Simplified for BYOC workflow)
