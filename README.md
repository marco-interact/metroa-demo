# COLMAP Demo - 3D Reconstruction Platform

A full-stack application for 3D reconstruction using COLMAP, featuring a modern Next.js frontend and FastAPI backend optimized for GPU processing.

![COLMAP Demo](https://img.shields.io/badge/COLMAP-3D%20Reconstruction-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.0.4-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.4-green)
![Python](https://img.shields.io/badge/Python-3.13-blue)

---

## 🚀 Quick Start

### For RunPod Deployment

```bash
curl -fsSL https://raw.githubusercontent.com/marco-interact/colmap-demo/main/runpod-setup.sh | bash
```

See [Quick Reference Guide](cursor-logs/2025-11-03/QUICK_REFERENCE.md) for detailed commands.

### Local Development

```bash
# Clone the repository
git clone https://github.com/marco-interact/colmap-demo.git
cd colmap-demo

# Backend setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"

# Start backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend setup (in a new terminal)
npm install
npm run dev
```

---

## 📋 Features

- ✨ **3D Reconstruction**: Upload images and generate 3D point clouds using COLMAP
- 🎨 **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- 🚀 **GPU Accelerated**: Optimized for CUDA-enabled GPUs on RunPod
- 📊 **Project Management**: Organize and manage multiple reconstruction projects
- 🔍 **3D Viewer**: Interactive Three.js-based 3D model viewer
- 🎯 **Demo Scans**: Pre-loaded demo projects for quick testing
- 💾 **Database Backed**: SQLite database for efficient project storage
- 🔄 **Real-time Processing**: Live updates during reconstruction

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Next.js 14.0.4
- React 18
- TypeScript
- Tailwind CSS
- Three.js / React Three Fiber
- Framer Motion

**Backend:**
- Python 3.13
- FastAPI
- COLMAP (Computer Vision)
- SQLite (aiosqlite)
- OpenCV
- NumPy

**Infrastructure:**
- RunPod (GPU Computing)
- Vercel (Frontend Hosting)
- Docker (Containerization)

### Project Structure

```
colmap-demo/
├── src/                      # Next.js frontend
│   ├── app/                  # App router pages
│   │   ├── api/             # API routes
│   │   ├── projects/        # Projects pages
│   │   └── dashboard/       # Dashboard
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── types/               # TypeScript types
├── main.py                  # FastAPI backend
├── database.py              # Database management
├── colmap_processor.py      # COLMAP processing
├── data/                    # Application data
│   ├── results/            # Processing results
│   ├── cache/              # Temporary cache
│   └── uploads/            # User uploads
├── demo-resources/          # Demo projects
├── scripts/                 # Utility scripts
├── cursor-logs/            # Development logs
└── config/                 # Configuration files
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env` or system environment):
```bash
STORAGE_DIR=/workspace/colmap-demo/data/results
DATABASE_PATH=/workspace/colmap-demo/data/database.db
CACHE_DIR=/workspace/colmap-demo/data/cache
UPLOADS_DIR=/workspace/colmap-demo/data/uploads
COLMAP_PATH=/usr/local/bin/colmap
PYTHONUNBUFFERED=1
```

**Frontend** (Vercel environment variables):
```bash
NEXT_PUBLIC_API_URL=http://your-runpod-endpoint.proxy.runpod.net
```

---

## 📦 Deployment

### RunPod (Backend)

Complete deployment guide available at:
- [Full Deployment Guide](cursor-logs/2025-11-03/RUNPOD_DEPLOYMENT_GUIDE.md)
- [Quick Reference](cursor-logs/2025-11-03/QUICK_REFERENCE.md)

**Current Pod Configuration:**
- Pod ID: `xhqt6a1roo8mrc`
- Storage: `rrtms4xkiz` (colmap-gpu-volume)
- Public Endpoint: `http://xhqt6a1roo8mrc-8000.proxy.runpod.net`

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd colmap-demo
npm install
npm run build
vercel --prod --scope interact-hq
```

**Vercel Configuration:**
- Team: interact-hq
- Team ID: `team_PWckdPO4Vl3C1PWOA9qs9DrI`

---

## 🛠️ Development

### Prerequisites

- Python 3.13+
- Node.js 18+
- COLMAP 3.9.1+
- CUDA-compatible GPU (for production)
- SQLite 3

### Install COLMAP

**Ubuntu/Debian:**
```bash
sudo apt-get install \
    cmake \
    ninja-build \
    build-essential \
    libboost-all-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev

git clone https://github.com/colmap/colmap.git
cd colmap
mkdir build && cd build
cmake .. -GNinja
ninja && sudo ninja install
```

**macOS:**
```bash
brew install colmap
```

### Running Tests

```bash
# Test COLMAP installation
colmap -h

# Test backend
curl http://localhost:8000/health

# Test reconstruction
cd scripts/test
./test-colmap-simple.sh
```

---

## 📚 API Documentation

### Base URL

**Local**: `http://localhost:8000`  
**Production**: `http://xhqt6a1roo8mrc-8000.proxy.runpod.net`

### Endpoints

#### Health Check
```http
GET /health
```

#### List Projects
```http
GET /api/projects
```

#### Get Project Details
```http
GET /api/projects/{project_id}
```

#### Upload Images
```http
POST /api/upload
Content-Type: multipart/form-data

Body: files (multiple image files)
```

#### Start Processing
```http
POST /api/process
Content-Type: application/json

Body: {
  "project_id": "string",
  "config": {
    "quality": "high|medium|low"
  }
}
```

#### Get Results
```http
GET /api/results/{result_id}
```

---

## 🔍 Demo Projects

The application includes three pre-loaded demo projects:

1. **Dollhouse** (`demoscan-dollhouse`)
   - First floor architectural scan
   - High-detail interior reconstruction

2. **Facade** (`demoscan-fachada`)
   - Building exterior scan
   - Large-scale architectural model

3. **Triangulos** (`demoscan-tiangulos`)
   - Complex geometric structures
   - Multi-angle reconstruction

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📝 Documentation

- [RunPod Deployment Guide](cursor-logs/2025-11-03/RUNPOD_DEPLOYMENT_GUIDE.md)
- [Quick Reference](cursor-logs/2025-11-03/QUICK_REFERENCE.md)
- [Cursor Logs](cursor-logs/) - Development history and notes

---

## 🐛 Troubleshooting

### Backend Issues

**COLMAP not found:**
```bash
export PATH="/path/to/colmap/bin:$PATH"
```

**Database errors:**
```bash
rm -f data/database.db
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
```

**Port in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Build errors:**
```bash
rm -rf node_modules .next
npm install
npm run build
```

**API connection issues:**
Check `NEXT_PUBLIC_API_URL` environment variable in Vercel.

---

## 📊 Performance

- **GPU Required**: CUDA-compatible GPU recommended for production
- **Memory**: Minimum 16GB RAM, 8GB VRAM
- **Storage**: SSD recommended, ~10GB per project
- **Processing Time**: Varies by project size (10-60 minutes typical)

---

## 🔒 Security

- All uploads are validated and scanned
- Database uses parameterized queries
- CORS configured for trusted origins
- File size limits enforced
- Temporary files automatically cleaned

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 👥 Team

**Organization**: Interact HQ  
**Repository**: https://github.com/marco-interact/colmap-demo  
**Contact**: [Your contact information]

---

## 🙏 Acknowledgments

- [COLMAP](https://colmap.github.io/) - Computer Vision library
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Three.js](https://threejs.org/) - 3D rendering library

---

**Last Updated**: 2025-11-03  
**Version**: 1.0.0

