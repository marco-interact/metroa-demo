# Metroa Labs - 3D Reconstruction Platform

Professional videogrammetry platform powered by COLMAP and Next.js. Upload videos, get high-quality 3D point clouds with measurement tools.

---

## 🚀 Quick Start

### Option 1: Docker Image (Recommended for Production)

**Pre-built GPU image with COLMAP + OpenMVS + Open3D**

```bash
# Build the image
make build
# or
./docker-build.sh

# Run locally (requires GPU)
docker run --gpus all -p 8888:8888 metroa-backend:latest

# Test health endpoint
curl http://localhost:8888/health
```

**For RunPod:**
1. Build and push image to your registry
2. Update RunPod template to use: `metroa-backend:latest`
3. Configure volumes: `/workspace/data` → persistent storage

See [INFRA.md](./INFRA.md) for detailed Docker documentation.

---

### Option 2: RunPod Script Setup (Legacy)

**Pod Specifications:**
- Pod ID: `8pexe48luksdw3`
- GPU: RTX 4090 (24GB VRAM)
- Volume: `metroa-volume` (mvmh2mg1pt)
- Port: 8888
- Container: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`

**Setup (Run once on new pod):**

```bash
# SSH into pod
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519

# Run master setup script
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo
bash setup-metroa-pod.sh
```

This script will:
1. Install system dependencies
2. Build COLMAP with RTX 4090 GPU support
3. Clone the repository
4. Setup Python environment
5. Configure persistent storage
6. Initialize database with demo data
7. Test GPU functionality
8. Start backend server on port 8888

**Backend URL:**
```
https://8pexe48luksdw3-8888.proxy.runpod.net
```

---

### Vercel Frontend Deployment

**Project:** `metroa-demo`  
**Team:** `interact-hq`

**Deploy:**

```bash
# On your local machine
cd /path/to/metroa-demo

# Set backend URL
echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production

# Deploy to Vercel
vercel --prod
```

---

## 🏗️ Architecture

```
User Browser
    ↓
Next.js Frontend (Vercel)
├── Three.js 3D Viewer
├── Measurement Tools
└── Project Management
    ↓
    Proxies to /api/backend
    ↓
FastAPI Backend (RunPod)
├── Video Upload Handler
├── COLMAP Processor
│   ├── Frame Extraction (Auto FPS)
│   ├── Feature Detection (GPU/CPU)
│   ├── Feature Matching (GPU/CPU)
│   ├── Sparse Reconstruction
│   └── Dense Reconstruction (10-100x more points!)
├── SQLite Database
└── File Storage (Persistent Volume)
```

---

## 🎯 Features

### 3D Reconstruction
- ✅ **Auto FPS Detection** - Adapts to video length
- ✅ **GPU Acceleration** - RTX 4090 support with CPU fallback
- ✅ **Dense Reconstruction** - 10-100x more points than sparse
- ✅ **Smart Quality Modes** - Low/Medium/High presets
- ✅ **Target: < 2 minutes** for 20-second videos

### 3D Viewer
- ✅ **WebGL Point Cloud Rendering** - Millions of points
- ✅ **Interactive Controls** - Rotate, zoom, pan
- ✅ **Measurement Tools** - Calibrated distance measurements
- ✅ **Color-Coded Selectors** - Blue (Point 1), Green (Point 2)
- ✅ **Performance Optimized** - Auto-downsampling for large clouds

### Measurement System
- ✅ **Scale Calibration** - Set known distance
- ✅ **Point Selection** - Visual feedback with indicators
- ✅ **Distance Calculation** - Real-world measurements
- ✅ **Export** - CSV/JSON measurement data

---

## 📁 Project Structure

```
metroa-demo/
├── main.py                    # FastAPI backend (port 8888)
├── database.py                # SQLite database layer
├── colmap_processor.py        # COLMAP pipeline with GPU support
├── colmap_binary_parser.py    # Measurement system
├── thumbnail_generator.py     # Thumbnail creation
├── requirements.txt           # Python dependencies
├── setup-metroa-pod.sh       # Master setup script for RunPod
├── build-colmap-gpu-fixed.sh  # COLMAP GPU build script
│
├── src/                       # Next.js frontend
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   │   ├── 3d/               # Three.js 3D viewers
│   │   ├── forms/            # Project/scan modals
│   │   └── ui/               # Shadcn UI components
│   ├── lib/                   # API client, utilities
│   └── types/                 # TypeScript definitions
│
├── demo-resources/            # Demo 3D models & thumbnails
├── data/                      # Persistent storage (symlinked to volume)
│   ├── results/              # Reconstruction outputs
│   ├── uploads/              # User video uploads
│   └── cache/                # Temporary files
│
├── package.json               # Node.js dependencies
├── next.config.js             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS
└── vercel.json                # Vercel deployment config
```

---

## 🔧 Technology Stack

### Backend
- **Python 3.12** - Runtime
- **FastAPI** - REST API framework
- **COLMAP 3.10** - 3D reconstruction engine
- **SQLite** - Database
- **FFmpeg** - Video frame extraction
- **CUDA 12.8** - GPU acceleration

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Three.js** - 3D rendering
- **React Three Fiber** - React wrapper for Three.js
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library

---

## 📊 Performance Targets

| Video Length | Frames | Processing Time | Point Cloud Size |
|--------------|--------|-----------------|------------------|
| 10 seconds | ~40 | **~1 minute** | 50K-500K points |
| 20 seconds | ~70 | **~2 minutes** | 100K-1M points |
| 60 seconds | ~70 | **~2 minutes** | 100K-1M points |

---

## 🛠️ Backend Commands

### Start/Stop Backend (RunPod)

```bash
# Start
cd /workspace/metroa-demo
bash setup-metroa-pod.sh

# Stop
kill $(cat /workspace/metroa-demo/backend.pid)

# View logs
tail -f /workspace/metroa-demo/backend.log

# Restart
kill $(cat backend.pid) 2>/dev/null || true
cd /workspace/metroa-demo
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

### Database Management

```bash
# Reinitialize database
cd /workspace/metroa-demo
source venv/bin/activate
python3 -c "from database import db; print(db.setup_demo_data())"

# Backup database
cp /workspace/data/database.db /workspace/data/database.backup.db

# View database
sqlite3 /workspace/data/database.db "SELECT * FROM projects;"
```

---

## 🌐 Frontend Commands

### Local Development

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

### Vercel Deployment

```bash
# Set backend URL
echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production

# Deploy
vercel --prod
```

---

## 🧪 Testing

### Backend Health Check

```bash
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health
```

Expected response:
```json
{"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}
```

### API Status

```bash
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/api/status
```

Expected:
```json
{
  "backend": "running",
  "projects_count": 1,
  "scans_count": 2,
  "projects": [{"id":"...","name":"Reconstruction Test Project 1"}]
}
```

---

## 📚 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - Backend status

### Projects & Scans
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/scans` - List project scans
- `GET /api/scans/{id}/details` - Get scan details
- `DELETE /api/scans/{id}` - Delete scan
- `POST /projects` - Create project

### Reconstruction
- `POST /api/reconstruction/upload` - Upload video for processing
- `GET /api/jobs/{id}` - Get processing job status
- `GET /api/point-cloud/{id}/stats` - Get point cloud statistics

### Measurements
- `POST /api/measurements/calibrate` - Calibrate scale
- `POST /api/measurements/add` - Add measurement
- `GET /api/measurements/{id}/export` - Export measurements
- `GET /api/measurements/{id}/stats` - Get reconstruction stats

---

## 🔍 Troubleshooting

### Backend Issues

**502 Bad Gateway:**
```bash
# Backend not running - start it
bash /workspace/metroa-demo/setup-metroa-pod.sh
```

**GPU not working:**
```bash
# Check GPU
nvidia-smi

# Test COLMAP GPU
QT_QPA_PLATFORM=offscreen colmap -h

# Backend will automatically fallback to CPU
```

**Database issues:**
```bash
# Reinitialize
cd /workspace/metroa-demo && source venv/bin/activate
python3 -c "from database import db; db.setup_demo_data()"
```

### Frontend Issues

**Can't connect to backend:**
```bash
# Check .env.production
cat .env.production

# Should be:
NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"

# Redeploy if wrong
vercel --prod
```

**3D Viewer slow/frozen:**
- Point clouds auto-downsample to 500K points
- Use requestIdleCallback for non-blocking loading
- Browser needs WebGL support

---

## 📦 Dependencies

### Python (requirements.txt)
- fastapi
- uvicorn
- numpy
- opencv-python
- pillow
- aiofiles

### Node.js (package.json)
- next
- react
- three
- @react-three/fiber
- @react-three/drei
- tailwindcss
- lucide-react

---

## 🎯 Demo Data

**Project:** Reconstruction Test Project 1  
**Scans:**
1. Dollhouse Scan (~1M points)

Demo files located in: `demo-resources/`

---

## 📞 Support

- **RunPod Dashboard:** https://www.runpod.io/console/pods
- **Vercel Dashboard:** https://vercel.com/interact-hq/metroa-demo
- **GitHub Repo:** https://github.com/marco-interact/metroa-demo
- **COLMAP Docs:** https://colmap.github.io/tutorial.html

---

## 📝 License

Proprietary - Interact HQ

---

## 🚀 Quick Reference

```bash
# RUNPOD COMMANDS (☁️ RunPod Terminal)
bash setup-metroa-pod.sh              # Setup everything
tail -f /workspace/metroa-demo/backend.log  # View logs
kill $(cat backend.pid)                # Stop backend

# LOCAL COMMANDS (📱 Mac Terminal)
vercel --prod                          # Deploy frontend
npm run dev                            # Local development
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health  # Test backend
```

**Ready for production!** 🎉
