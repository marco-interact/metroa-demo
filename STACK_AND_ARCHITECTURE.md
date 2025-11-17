# Metroa Demo - Stack & Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                    (WebGL-enabled browser)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Vercel)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React 18 + TypeScript                                   │   │
│  │  ├── Three.js / React Three Fiber (3D Viewer)           │   │
│  │  ├── Tailwind CSS (Styling)                             │   │
│  │  ├── Shadcn UI (Components)                             │   │
│  │  └── React Hook Form + Zod (Forms)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │ API Proxy                             │
│                          │ /api/backend/*                        │
└──────────────────────────┼─────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (RunPod GPU Pod)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Python 3.12 + FastAPI 0.115.4                          │   │
│  │  ├── Video Upload Handler                                │   │
│  │  ├── COLMAP Processor (3D Reconstruction)               │   │
│  │  ├── OpenMVS Processor (Ultra Densification)            │   │
│  │  ├── Open3D Post-Processing                             │   │
│  │  ├── Measurement System                                  │   │
│  │  └── SQLite Database                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────┴──────────────────────────────────┐   │
│  │  GPU: RTX 4090 (24GB VRAM)                               │   │
│  │  CUDA 12.8.1                                             │   │
│  │  Persistent Storage: /workspace/data (50GB volume)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack

### Frontend Stack

#### Core Framework
- **Next.js 14.2.0** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5** - Type safety

#### 3D Rendering
- **Three.js 0.159.0** - WebGL 3D graphics library
- **@react-three/fiber 8.18.0** - React renderer for Three.js
- **@react-three/drei 9.122.0** - Useful helpers for React Three Fiber
- **three-stdlib 2.36.0** - Three.js standard library utilities

#### UI & Styling
- **Tailwind CSS 3.3.0** - Utility-first CSS framework
- **@tailwindcss/forms 0.5.10** - Form styling plugin
- **@tailwindcss/typography 0.5.10** - Typography plugin
- **Shadcn UI** - Component library (Radix UI primitives)
- **Lucide React 0.294.0** - Icon library
- **Framer Motion 12.23.22** - Animation library

#### Forms & Validation
- **React Hook Form 7.48.2** - Form state management
- **Zod 3.22.4** - Schema validation
- **@hookform/resolvers 3.3.2** - Zod integration

#### Maps (if used)
- **Leaflet 1.9.4** - Interactive maps
- **React Leaflet 4.2.1** - React wrapper for Leaflet

#### Build Tools
- **PostCSS 8** - CSS processing
- **Autoprefixer 10.0.1** - CSS vendor prefixing
- **ESLint** - Code linting
- **Prettier 3.1.1** - Code formatting

---

### Backend Stack

#### Web Framework
- **Python 3.12** - Runtime
- **FastAPI 0.115.4** - Modern async web framework
- **Uvicorn 0.32.0** - ASGI server
- **Python Multipart 0.0.12** - File upload handling

#### 3D Reconstruction Engines
- **COLMAP 3.10** - Structure-from-Motion pipeline
  - CUDA-enabled (GPU acceleration)
  - RTX 4090 optimized (compute capability 8.9)
  - Sparse & Dense reconstruction
- **OpenMVS v2.2.0** - Multi-view stereo densification
  - DensifyPointCloud
  - ReconstructMesh
  - InterfaceCOLMAP (COLMAP converter)
- **Open3D 0.19.0** - Point cloud processing
  - Outlier removal
  - Statistical filtering
  - Downsampling
  - Point cloud cleaning

#### Computer Vision & Processing
- **OpenCV Python 4.10.0.84** - Image processing
- **NumPy 1.26.4** - Numerical computing
- **PyTorch >=2.2.0** - Deep learning (for custom feature matching)
- **FFmpeg** - Video frame extraction

#### Database
- **SQLite 3** - Embedded database
- **aiosqlite 0.20.0** - Async SQLite driver

#### Utilities
- **Pydantic 2.9.2** - Data validation
- **Pydantic Settings 2.6.0** - Settings management
- **Python Dotenv 1.0.1** - Environment variables
- **tqdm 4.66.5** - Progress bars

---

### Infrastructure & Deployment

#### Containerization
- **Docker** - Container runtime
- **Base Image:** `nvidia/cuda:12.8.1-devel-ubuntu24.04`
- **Multi-stage builds** for COLMAP & OpenMVS

#### Cloud Platforms
- **Vercel** - Frontend hosting (Next.js)
- **RunPod** - GPU backend hosting
  - Pod: RTX 4090 (24GB VRAM)
  - Persistent Volume: 50GB
  - Port: 8888

#### Storage
- **Persistent Volume** (`/workspace/data`)
  - `database.db` - SQLite database
  - `results/{scan_id}/` - Reconstruction outputs
  - `uploads/{scan_id}/` - User video uploads
  - `cache/` - Temporary files

---

## 🔄 Processing Pipeline

### Video Upload → 3D Point Cloud

```
1. Video Upload
   └─> /workspace/data/uploads/{scan_id}/video.mp4

2. Frame Extraction (FFmpeg)
   └─> /workspace/data/results/{scan_id}/images/*.jpg
   └─> Auto FPS detection (2-8 fps based on video length)

3. Feature Extraction (COLMAP SIFT)
   └─> GPU-accelerated (CUDA) or CPU fallback
   └─> Quality-dependent: 8K-16K+ features per image

4. Feature Matching (COLMAP)
   └─> GPU-accelerated matching
   └─> Sequential or exhaustive matching based on quality

5. Sparse Reconstruction (COLMAP)
   └─> /workspace/data/results/{scan_id}/sparse/0/
   └─> cameras.bin, images.bin, points3D.bin
   └─> Typically 10K-100K sparse points

6. Dense Reconstruction (COLMAP or OpenMVS)
   ├─> COLMAP Dense (fast/high_quality modes)
   │   └─> Patch Match Stereo
   │   └─> Stereo Fusion
   │   └─> /workspace/data/results/{scan_id}/dense/fused.ply
   │
   └─> OpenMVS DensifyPointCloud (ultra_openmvs mode)
       └─> Export COLMAP → OpenMVS format
       └─> DensifyPointCloud processing
       └─> /workspace/data/results/{scan_id}/openmvs/scene_dense.ply

7. Post-Processing (Open3D)
   └─> Statistical outlier removal
   └─> Downsampling (if >5M points)
   └─> /workspace/data/results/{scan_id}/pointcloud_final.ply

8. Export to Frontend
   └─> PLY file served via FastAPI static files
   └─> Loaded in Three.js viewer
```

---

## 🎯 Quality Modes

### `fast`
- **Frames:** 2-4 fps, 1280-1600px
- **Features:** 8K-10K per image
- **Matching:** Sequential
- **Dense:** COLMAP (1600-2000px, moderate iterations)
- **Post-processing:** Light cleanup
- **Target:** < 1 minute for 20s video
- **Points:** 50K-500K

### `high_quality`
- **Frames:** 6-8 fps, 1920-3200px
- **Features:** 16K+ per image
- **Matching:** Exhaustive with affine shape
- **Dense:** COLMAP (3200-4096px, 10-12 iterations)
- **Post-processing:** Statistical outlier removal
- **Target:** ~2 minutes for 20s video
- **Points:** 100K-1M

### `ultra_openmvs`
- **Frames:** 6-8 fps, 1920-3200px
- **Features:** Robust settings for poses
- **Matching:** Exhaustive
- **Dense:** OpenMVS DensifyPointCloud
- **Post-processing:** Mandatory cleanup, downsampling if >5M
- **Target:** ~5-10 minutes for 20s video
- **Points:** 500K-5M+

---

## 📊 Database Schema

### Tables

#### `users`
- `id` (TEXT PRIMARY KEY)
- `email` (TEXT UNIQUE)
- `name` (TEXT)
- `created_at` (TIMESTAMP)

#### `projects`
- `id` (TEXT PRIMARY KEY)
- `user_id` (TEXT FOREIGN KEY)
- `name` (TEXT)
- `description` (TEXT)
- `location` (TEXT)
- `space_type` (TEXT)
- `project_type` (TEXT)
- `status` (TEXT DEFAULT 'active')
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### `scans`
- `id` (TEXT PRIMARY KEY)
- `project_id` (TEXT FOREIGN KEY)
- `name` (TEXT)
- `status` (TEXT) - pending, processing, completed, failed
- `video_filename` (TEXT)
- `video_size` (INTEGER)
- `processing_quality` (TEXT) - Legacy: low/medium/high/ultra
- `quality_mode` (TEXT) - New: fast/high_quality/ultra_openmvs
- `ply_file` (TEXT) - Raw PLY path
- `pointcloud_final_path` (TEXT) - Final cleaned PLY
- `point_count_raw` (INTEGER)
- `point_count_final` (INTEGER)
- `postprocessing_stats` (TEXT JSON)
- `progress` (INTEGER 0-100)
- `current_stage` (TEXT)
- `is_360` (INTEGER) - 360° video flag
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### `reconstruction_metrics`
- `scan_id` (TEXT PRIMARY KEY)
- `quality_mode` (TEXT)
- `sparse_points` (INTEGER)
- `dense_points` (INTEGER)
- `registered_images` (INTEGER)
- `total_images` (INTEGER)
- `avg_reproj_error` (REAL)
- `avg_track_length` (REAL)
- `coverage_percentage` (REAL)
- `processing_time_seconds` (REAL)
- `quality_grade` (TEXT)

---

## 🌐 API Architecture

### Frontend → Backend Communication

```
Frontend (Next.js)
  └─> API Routes (/api/backend/*)
      └─> Next.js Rewrites
          └─> Backend URL (RunPod)
              └─> FastAPI Endpoints
```

### Key API Endpoints

#### Health & Status
- `GET /health` - Health check
- `GET /api/status` - Backend status with counts

#### Projects
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/scans` - List project scans
- `POST /projects` - Create project

#### Scans
- `GET /api/scans/{id}/details` - Get scan details
- `DELETE /api/scans/{id}` - Delete scan

#### Reconstruction
- `POST /api/reconstruction/upload` - Upload video
- `GET /api/jobs/{id}` - Get job status with progress
- `GET /api/reconstruction/{id}/statistics` - Get metrics
- `GET /api/point-cloud/{id}/stats` - Point cloud stats

#### Measurements
- `POST /api/measurements/calibrate` - Calibrate scale
- `POST /api/measurements/add` - Add measurement
- `GET /api/measurements/{id}/export` - Export measurements
- `GET /api/measurements/{id}/stats` - Reconstruction stats

#### File Serving
- `/demo-resources/*` - Static demo files
- `/results/*` - User reconstruction outputs

---

## 🔧 Development Environment

### Frontend Development
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (localhost:3000)
npm run build        # Build for production
npm run lint         # Run ESLint
```

### Backend Development
```bash
# Python virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

### Docker Development
```bash
# Build image
docker build -t metroa-backend:latest .

# Run with GPU
docker run --gpus all -p 8888:8888 metroa-backend:latest
```

---

## 📁 Project Structure

```
metroa-demo/
├── src/                          # Next.js frontend
│   ├── app/                      # App Router pages
│   │   ├── api/                  # API route handlers
│   │   ├── auth/                 # Authentication
│   │   ├── dashboard/            # Dashboard page
│   │   ├── projects/             # Project pages
│   │   └── layout.tsx            # Root layout
│   ├── components/               # React components
│   │   ├── 3d/                   # Three.js viewers
│   │   ├── forms/                # Form components
│   │   ├── layout/               # Layout components
│   │   └── ui/                   # Shadcn UI components
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # API client
│   │   └── utils.ts              # Helper functions
│   └── types/                    # TypeScript definitions
│
├── main.py                       # FastAPI backend entry point
├── database.py                   # SQLite database layer
├── colmap_processor.py           # COLMAP pipeline
├── colmap_binary_parser.py       # Measurement system
├── openmvs_processor.py          # OpenMVS integration
├── pointcloud_postprocess.py      # Open3D post-processing
├── quality_presets.py            # Quality mode configurations
├── opencv_sfm.py                 # OpenCV SfM (optional)
├── video_360_converter.py        # 360° video support
├── ply_to_gltf.py                # GLTF export
├── thumbnail_generator.py        # Thumbnail generation
│
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
├── Dockerfile                    # Docker image definition
├── next.config.js                # Next.js configuration
├── tsconfig.json                 # TypeScript configuration
├── tailwind.config.ts            # Tailwind CSS config
│
├── demo-resources/               # Demo 3D models & assets
├── data/                         # Persistent storage (symlinked)
│   ├── results/                  # Reconstruction outputs
│   ├── uploads/                  # User uploads
│   └── cache/                    # Temporary files
│
└── README/                       # Documentation
    └── 2025-11-14/
        ├── PIPELINE_ARCHITECTURE.md
        ├── INFRA.md
        └── ...
```

---

## 🚀 Deployment

### Frontend (Vercel)
- **Platform:** Vercel
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Environment Variables:**
  - `NEXT_PUBLIC_API_URL` - Backend API URL

### Backend (RunPod)
- **Platform:** RunPod GPU Pod
- **Container:** Docker image with COLMAP + OpenMVS
- **GPU:** RTX 4090 (24GB VRAM)
- **Port:** 8888
- **Volume:** Persistent 50GB volume at `/workspace/data`
- **Start Command:** `python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8888`

---

## 🔐 Security & Configuration

### Environment Variables

#### Backend
- `DATABASE_PATH` - SQLite database path (default: `/workspace/database.db`)
- `QT_QPA_PLATFORM=offscreen` - Headless GUI mode
- `DISPLAY=:99` - Virtual display
- `MESA_GL_VERSION_OVERRIDE=3.3` - OpenGL version override

#### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `PORT` - Server port (default: 3000)

### CORS
- Backend allows all origins (`allow_origins=["*"]`)
- Configured via FastAPI CORS middleware

---

## 📈 Performance Characteristics

### Processing Times (20-second video)
- **Fast Mode:** ~1 minute
- **High Quality:** ~2 minutes
- **Ultra OpenMVS:** ~5-10 minutes

### Point Cloud Sizes
- **Fast:** 50K-500K points
- **High Quality:** 100K-1M points
- **Ultra OpenMVS:** 500K-5M+ points

### GPU Utilization
- **COLMAP Feature Extraction:** ~80-90% GPU usage
- **COLMAP Matching:** ~60-70% GPU usage
- **Dense Reconstruction:** ~90-100% GPU usage
- **OpenMVS:** ~70-80% GPU usage

---

## 🔗 External Dependencies

### System Libraries (via apt)
- CUDA 12.8.1 toolkit
- Eigen3 (linear algebra)
- Ceres Solver (optimization)
- Boost (C++ libraries)
- OpenCV (image processing)
- FFmpeg (video processing)
- SQLite3 (database)

### Python Packages (via pip)
- See `requirements.txt` for complete list

### Node.js Packages (via npm)
- See `package.json` for complete list

---

## 📚 Key Documentation Files

- `README.md` - Main project documentation
- `README/2025-11-14/PIPELINE_ARCHITECTURE.md` - Processing pipeline details
- `README/2025-11-14/INFRA.md` - Infrastructure & Docker setup
- `STACK_AND_ARCHITECTURE.md` - This file

---

## 🎯 Summary

**Metroa Demo** is a full-stack 3D reconstruction platform:

- **Frontend:** Next.js + React + Three.js (deployed on Vercel)
- **Backend:** FastAPI + COLMAP + OpenMVS + Open3D (deployed on RunPod GPU)
- **Database:** SQLite (embedded)
- **Storage:** Persistent volume on RunPod
- **Processing:** GPU-accelerated 3D reconstruction from video
- **Output:** High-quality point clouds with measurement tools

The system processes video uploads through a multi-stage pipeline (frame extraction → feature detection → sparse reconstruction → dense reconstruction → post-processing) to produce accurate 3D point clouds that can be viewed and measured in a web-based 3D viewer.

