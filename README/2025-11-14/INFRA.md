# 🏗️ Infrastructure Documentation - Metroa Backend GPU Image

**Production-ready Docker image for RunPod deployment**

---

## 📋 Overview

The Metroa backend runs in a GPU-enabled Docker container with:

- **COLMAP 3.10** - Sparse and dense 3D reconstruction (CUDA-enabled)
- **OpenMVS v2.2.0** - Ultra-densification pipeline
- **Open3D 0.19.0** - Point cloud post-processing (Python)
- **Python 3.12** - FastAPI runtime environment
- **CUDA 12.8.1** - GPU acceleration support

---

## 🐳 Base Image

**Image:** `nvidia/cuda:12.8.1-devel-ubuntu24.04`

**Rationale:**
- CUDA 12.8.1 matches RunPod's GPU runtime
- Ubuntu 24.04 provides modern system libraries
- Development image includes CUDA toolkit + headers needed for building COLMAP/OpenMVS

---

## 📦 Installed Components

### COLMAP 3.10

**Source:** https://github.com/colmap/colmap (tag: `3.10`)

**Build Configuration:**
- CUDA enabled (`-DCUDA_ENABLED=ON`)
- RTX 4090 optimized (compute capability 8.9)
- Headless mode (GUI disabled)
- Fast math optimizations

**Installation Path:** `/usr/local/bin/colmap`

**Verification:**
```bash
colmap --help
ldd $(which colmap) | grep cuda  # Should show CUDA libraries
```

### OpenMVS v2.2.0

**Source:** https://github.com/cdcseacave/openMVS (tag: `v2.2.0`)

**Tools Installed:**
- `DensifyPointCloud` - Creates dense point clouds from sparse reconstruction
- `ReconstructMesh` - Generates mesh from point cloud
- `RefineMesh` - Refines mesh quality
- `TextureMesh` - Applies textures to mesh
- `InterfaceCOLMAP` - Converts COLMAP to OpenMVS format

**Installation Path:** `/usr/local/bin/`

**Verification:**
```bash
DensifyPointCloud --help
ReconstructMesh --help
```

### Open3D 0.19.0

**Installation:** Via pip (from `requirements.txt`)

**Usage:** Python bindings for point cloud processing

**Verification:**
```bash
python3.12 -c "import open3d; print(open3d.__version__)"
```

---

## 🔨 Building the Image

### Prerequisites

- Docker with BuildKit enabled
- NVIDIA Docker runtime (for GPU support)
- ~20GB free disk space
- ~30-45 minutes build time

### Quick Build

```bash
# Build with default tag (latest)
./docker-build.sh

# Build with specific tag
./docker-build.sh v1.0.0

# Build and push to registry
./docker-build.sh v1.0.0 --push
```

### Manual Build

```bash
docker build \
    --tag metroa-backend:latest \
    --file Dockerfile \
    --progress=plain \
    .
```

### Build Stages

The Dockerfile uses multi-stage builds:

1. **base** - CUDA base + system dependencies
2. **colmap-builder** - Builds COLMAP with CUDA
3. **openmvs-builder** - Builds OpenMVS tools
4. **production** - Final image with all components

---

## 🚀 Running the Container

### Local Testing (with GPU)

```bash
docker run --gpus all \
    -p 8888:8888 \
    -v /path/to/data:/workspace/data \
    metroa-backend:latest
```

### RunPod Configuration

**Container Image:** `metroa-backend:latest` (or your registry path)

**GPU:** Required (RTX 4090 or compatible)

**Ports:**
- `8888` - FastAPI backend

**Volumes:**
- `/workspace/data` - Persistent storage for:
  - Database (`database.db`)
  - Results (`results/`)
  - Uploads (`uploads/`)
  - Cache (`cache/`)

**Environment Variables:**
```bash
QT_QPA_PLATFORM=offscreen
DISPLAY=:99
MESA_GL_VERSION_OVERRIDE=3.3
DATABASE_PATH=/workspace/data/database.db
```

---

## ✅ Verification

### Check Installed Tools

```bash
# COLMAP
colmap --help | head -5
ldd $(which colmap) | grep cuda

# OpenMVS
DensifyPointCloud --help
ReconstructMesh --help

# Open3D
python3.12 -c "import open3d; print(open3d.__version__)"

# Python packages
python3.12 -c "import fastapi; print(fastapi.__version__)"
```

### Test GPU Access

```bash
nvidia-smi
python3.12 -c "import torch; print(torch.cuda.is_available())"
```

### Test Backend

```bash
# Start backend
python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8888

# Test health endpoint
curl http://localhost:8888/health
```

---

## 📊 Image Size

**Expected Size:** ~8-12 GB

**Breakdown:**
- Base CUDA image: ~4 GB
- COLMAP build: ~2 GB
- OpenMVS build: ~1 GB
- Python packages: ~1 GB
- System libraries: ~2 GB

---

## 🔄 Updating Versions

### Update COLMAP

Edit `Dockerfile`, change:
```dockerfile
ENV COLMAP_VERSION=3.10
```

### Update OpenMVS

Edit `Dockerfile`, change:
```dockerfile
ENV OPENMVS_VERSION=v2.2.0
```

### Update Open3D

Edit `requirements.txt`, change:
```
open3d==0.19.0
```

Then rebuild the image.

---

## 🐛 Troubleshooting

### Build Fails: CUDA Not Found

**Issue:** CMake can't find CUDA during COLMAP build

**Fix:** Ensure base image has CUDA toolkit:
```dockerfile
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04
```

### Build Fails: OpenMVS VCG Error

**Issue:** VCG library not found

**Fix:** Ensure submodules are cloned:
```dockerfile
git clone --recursive https://github.com/cdcseacave/openMVS.git
```

### Runtime: GPU Not Available

**Issue:** `nvidia-smi` fails in container

**Fix:** Run with `--gpus all` flag:
```bash
docker run --gpus all metroa-backend:latest
```

### Runtime: Open3D Import Error

**Issue:** `ImportError: libGL.so.1`

**Fix:** Ensure headless OpenGL libraries are installed:
```dockerfile
libegl1-mesa-dev libgles2-mesa-dev
```

---

## 📝 Version History

| Version | COLMAP | OpenMVS | Open3D | CUDA | Date |
|---------|--------|---------|--------|------|------|
| 1.0.0   | 3.10   | v2.2.0  | 0.19.0 | 12.8.1 | 2025-11-13 |

---

## 🔗 References

- [COLMAP Documentation](https://colmap.github.io/)
- [OpenMVS GitHub](https://github.com/cdcseacave/openMVS)
- [Open3D Documentation](http://www.open3d.org/docs/)
- [NVIDIA CUDA Docker](https://hub.docker.com/r/nvidia/cuda)
- [RunPod Documentation](https://docs.runpod.io/)

---

## 📧 Support

For infrastructure issues, check:
1. Build logs: `docker build` output
2. Runtime logs: Container stdout/stderr
3. Health endpoint: `curl http://localhost:8888/health`

