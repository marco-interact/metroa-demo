# Metroa Labs - 3D Reconstruction Platform

Professional videogrammetry platform powered by COLMAP and Next.js. Upload videos, get high-quality 3D point clouds with measurement tools.

---

## 🎯 **What is Metroa?**

Upload a video → Get a 3D point cloud → Measure distances → Download results

**Key Features:**
- ✅ GPU-accelerated 3D reconstruction (COLMAP)
- ✅ Real-time point cloud viewer (Three.js)
- ✅ Distance measurement tools
- ✅ First-person navigation
- ✅ High-quality mesh generation
- ✅ Mobile-optimized interface

---

## 🚀 **Quick Start**

### **1. Build Docker Image (Local)**

```bash
cd /path/to/metroa-demo

# Build (5-10 minutes)
bash docker-build-local.sh
# Select option 1 (Fast Build)

# Test locally
docker run -d -p 8888:8888 metroa-backend:fast
curl http://localhost:8888/health
```

### **2. Push to Docker Hub**

```bash
docker login
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest
```

### **3. Deploy Backend on RunPod**

1. Go to [RunPod](https://runpod.io)
2. Click **Deploy**
3. Select **RTX 4090** GPU
4. **Container Image:** `YOUR_USERNAME/metroa-backend:latest`
5. **Expose HTTP Ports:** `8888`
6. **Container Disk:** 50 GB
7. **Network Volume:** None (not needed)
8. Click **Deploy**

**Access:** `https://YOUR-POD-ID-8888.proxy.runpod.net/health`

### **4. Deploy Frontend on Vercel**

```bash
# Update .env.production with your RunPod URL
echo 'NEXT_PUBLIC_API_URL="https://YOUR-POD-ID-8888.proxy.runpod.net"' > .env.production

# Deploy
vercel --prod
```

**Done!** Your app is live.

---

## 📚 **Documentation**

### **Essential Guides:**
- **[RunPod Docker Guide](RUNPOD_DOCKER_GUIDE.md)** - Complete backend deployment
- **[Docker Quickstart](DOCKER_QUICKSTART.md)** - Quick Docker reference
- **[Vercel Deploy](README/deployment/VERCEL_DEPLOY.md)** - Frontend deployment
- **[Documentation Index](README/INDEX.md)** - All guides

### **Technical Guides:**
- [Stack & Architecture](README/guides/STACK_AND_ARCHITECTURE.md)
- [Processing Workflow](README/guides/PROCESSING_WORKFLOW.md)
- [Reconstruction Optimization](README/guides/RECONSTRUCTION_OPTIMIZATION_GUIDE.md)
- [Mesh Generation](README/guides/MESH_GENERATION_GUIDE.md)

---

## 🏗️ **Architecture**

```
Frontend (Next.js)          Backend (FastAPI)           GPU Processing
─────────────────          ─────────────────           ──────────────
┌───────────────┐          ┌───────────────┐          ┌─────────────┐
│   React UI    │  HTTP    │  FastAPI      │  Calls   │   COLMAP    │
│   Three.js    ├────────→ │  Endpoints    ├────────→ │   (CUDA)    │
│   Tailwind    │          │  SQLite DB    │          │   OpenMVS   │
└───────────────┘          └───────────────┘          │   Open3D    │
                                                       └─────────────┘
Deployed on:               Deployed on:                Runs in:
Vercel                     RunPod (Docker)             Docker Container
```

---

## 🛠️ **Tech Stack**

### **Frontend**
- Next.js 15 (React 19)
- TypeScript
- Three.js (3D rendering)
- Tailwind CSS
- Zustand (state management)

### **Backend**
- Python 3.12
- FastAPI
- COLMAP 3.x (GPU-accelerated)
- Open3D 0.19.0
- OpenCV 4.10.0
- SQLite

### **Infrastructure**
- Docker (containerization)
- RunPod (GPU hosting)
- Vercel (frontend hosting)
- Docker Hub (image registry)

---

## 📁 **Project Structure**

```
metroa-demo/
├── src/                          # Frontend (Next.js)
│   ├── app/                      # App routes
│   ├── components/               # React components
│   │   ├── 3d/                   # 3D viewer components
│   │   └── ui/                   # UI components
│   └── lib/                      # Utilities
│
├── *.py                          # Backend (FastAPI)
│   ├── main.py                   # API server entry point
│   ├── colmap_processor.py       # COLMAP 3D reconstruction
│   ├── mesh_generator.py         # Mesh generation
│   ├── database.py               # SQLite database
│   └── video_analyzer.py         # Video processing
│
├── Dockerfile                    # Production build (30-45 min)
├── Dockerfile.fast               # Fast build (5-10 min) ⭐
├── docker-build-local.sh         # Build script ⭐
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
│
├── README.md                     # This file
├── RUNPOD_DOCKER_GUIDE.md        # Main deployment guide ⭐
├── DOCKER_QUICKSTART.md          # Quick reference
└── README/                       # Additional documentation
    ├── deployment/               # Deployment guides
    └── guides/                   # Technical guides
```

---

## 🔧 **Development**

### **Backend (Python)**

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires COLMAP installed)
python main.py

# API will be at http://localhost:8888
```

### **Frontend (Next.js)**

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Open http://localhost:3000
```

### **Docker (Recommended)**

```bash
# Build image
bash docker-build-local.sh

# Run container
docker run -d -p 8888:8888 -p 3000:3000 metroa-backend:fast

# View logs
docker logs -f $(docker ps -q)
```

---

## 🌐 **Deployment**

### **Backend: RunPod**
1. Build Docker image locally
2. Push to Docker Hub
3. Deploy on RunPod using image
4. No persistent storage needed!

**Full guide:** [RUNPOD_DOCKER_GUIDE.md](RUNPOD_DOCKER_GUIDE.md)

### **Frontend: Vercel**
```bash
vercel --prod
```

**Full guide:** [README/deployment/VERCEL_DEPLOY.md](README/deployment/VERCEL_DEPLOY.md)

---

## 📊 **Performance**

### **Processing Times (RTX 4090)**
| Video Length | Frames | Point Cloud | Mesh | Total Time |
|-------------|--------|-------------|------|------------|
| 30 seconds  | 300    | ~500K pts   | 1-2 min | ~3-5 min |
| 1 minute    | 600    | ~1M pts     | 2-3 min | ~5-8 min |
| 2 minutes   | 1200   | ~2M pts     | 4-6 min | ~10-15 min |

### **GPU Utilization**
- COLMAP feature extraction: 80-95% GPU
- Dense reconstruction: 90-99% GPU
- Mesh generation: 60-80% GPU

---

## 🧪 **API Endpoints**

```bash
# Health check
GET /health

# Upload video
POST /api/scans/upload

# Process scan
POST /api/scans/{scan_id}/process

# Get results
GET /api/scans/{scan_id}

# Download point cloud
GET /api/scans/{scan_id}/download/ply
```

**Full API docs:** http://YOUR-POD-URL/docs

---

## 🎯 **Roadmap**

- [x] COLMAP GPU integration
- [x] Point cloud viewer
- [x] Distance measurements
- [x] First-person navigation
- [x] Mesh generation
- [x] Mobile optimization
- [ ] Multi-camera calibration
- [ ] Real-time preview
- [ ] Cloud storage integration
- [ ] Batch processing
- [ ] Advanced mesh texturing

---

## 📝 **License**

Proprietary - Metroa Labs

---

## 🆘 **Support**

- **Documentation:** [README/INDEX.md](README/INDEX.md)
- **RunPod Guide:** [RUNPOD_DOCKER_GUIDE.md](RUNPOD_DOCKER_GUIDE.md)
- **Docker Guide:** [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

---

## 🙏 **Acknowledgments**

Built with:
- [COLMAP](https://colmap.github.io/) - 3D reconstruction
- [Open3D](http://www.open3d.org/) - 3D data processing
- [Three.js](https://threejs.org/) - 3D rendering
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python API framework

---

**Ready to get started?** → [RUNPOD_DOCKER_GUIDE.md](RUNPOD_DOCKER_GUIDE.md)
