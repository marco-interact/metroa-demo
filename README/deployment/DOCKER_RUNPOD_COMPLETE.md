# 🐳 Complete Docker Setup for RunPod

## Overview

This guide provides a **bulletproof Docker workflow** for running Metroa on RunPod with:
- ✅ COLMAP 3.10 (GPU-accelerated, built from source)
- ✅ OpenMVS v2.2.0 (ultra-dense point clouds)
- ✅ Open3D 0.19.0 (point cloud processing)
- ✅ Full Python stack (FastAPI, OpenCV, etc.)

**Build once, run forever!**

---

## 🚀 Quick Start (2 Commands)

```bash
# SSH into RunPod, then:
cd /workspace/metroa-demo

# 1. Pull latest code
git pull origin main

# 2. Build Docker image (30-45 min, one-time)
bash README/scripts/build-docker-runpod.sh

# 3. Run container (starts in seconds)
bash README/scripts/run-docker-runpod.sh
```

**That's it!** Backend will be running at `http://localhost:8888`

---

## 📋 What Gets Built

### Docker Image Contents

The build creates a production-ready image with:

| Component | Version | Purpose | Build Time |
|-----------|---------|---------|------------|
| **COLMAP** | 3.10 | Structure from Motion (GPU) | ~20 min |
| **OpenMVS** | v2.2.0 | Dense reconstruction | ~10 min |
| **Open3D** | 0.19.0 | Point cloud processing | ~5 min |
| **Python** | 3.12 | Runtime environment | ~5 min |
| **CUDA** | 12.8.1 | GPU acceleration | Base image |

**Total size:** ~8-12 GB  
**Total time:** 30-45 minutes (one-time only!)

---

## 🔨 Step 1: Build Docker Image

### Automated Build Script

```bash
cd /workspace/metroa-demo
bash README/scripts/build-docker-runpod.sh
```

**What the script does:**
1. ✅ Checks prerequisites (disk space, GPU, Docker daemon)
2. ✅ Cleans up old containers/images
3. ✅ Builds Docker image with progress output
4. ✅ Verifies COLMAP, OpenMVS, Python packages
5. ✅ Test-runs the container
6. ✅ Provides next steps

### Manual Build (if needed)

```bash
cd /workspace/metroa-demo

# Ensure Docker daemon is running
dockerd > /dev/null 2>&1 &
sleep 5

# Build image
docker build -t metroa-backend:latest .

# This takes 30-45 minutes - be patient!
```

---

## 🚀 Step 2: Run Docker Container

### Automated Run Script

```bash
cd /workspace/metroa-demo
bash README/scripts/run-docker-runpod.sh
```

**What the script does:**
1. ✅ Starts Docker daemon (if needed)
2. ✅ Cleans up old containers
3. ✅ Creates data directories
4. ✅ Starts container with GPU support
5. ✅ Tests health endpoint
6. ✅ Shows access URLs and commands

### Manual Run (if needed)

```bash
# Start Docker daemon
dockerd > /dev/null 2>&1 &
sleep 5

# Create data directories
mkdir -p /workspace/metroa-demo/data/{uploads,results,cache}

# Run container
docker run -d \
  --name metroa-backend \
  --gpus all \
  --restart unless-stopped \
  -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend:latest

# Wait for startup
sleep 15

# Test
curl http://localhost:8888/health
```

---

## 🧪 Verification

After running, verify everything works:

```bash
# 1. Check container is running
docker ps --filter name=metroa-backend

# 2. Test health endpoint
curl http://localhost:8888/health
# Should return: {"status":"healthy","gpu_available":true,...}

# 3. Check logs
docker logs metroa-backend --tail 50

# 4. Test COLMAP inside container
docker exec metroa-backend colmap --version

# 5. Test OpenMVS inside container
docker exec metroa-backend DensifyPointCloud --help
```

---

## 📊 Container Management

### View Logs

```bash
# Live logs (follow)
docker logs -f metroa-backend

# Last 50 lines
docker logs metroa-backend --tail 50

# Last 5 minutes
docker logs metroa-backend --since 5m

# Save logs to file
docker logs metroa-backend > backend-logs.txt
```

### Control Container

```bash
# Stop container
docker stop metroa-backend

# Start container (if stopped)
docker start metroa-backend

# Restart container
docker restart metroa-backend

# Remove container (keeps image)
docker rm -f metroa-backend

# Check container status
docker ps --filter name=metroa-backend
```

### Shell Access

```bash
# Open bash shell in container
docker exec -it metroa-backend bash

# Once inside:
colmap --version
python3.12 -c "import open3d; print(open3d.__version__)"
ls -la /workspace/data/
exit
```

---

## 💾 Save & Share Image

### Save Image to File

```bash
# Save to compressed archive
docker save metroa-backend:latest | gzip > metroa-backend.tar.gz

# Size: ~4-6 GB compressed

# Load on another machine
gunzip -c metroa-backend.tar.gz | docker load
```

### Push to Docker Hub (Recommended)

```bash
# 1. Login to Docker Hub
docker login

# 2. Tag image with your username
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest

# 3. Push to Docker Hub
docker push YOUR_USERNAME/metroa-backend:latest

# 4. Pull on any RunPod instance
docker pull YOUR_USERNAME/metroa-backend:latest
docker run -d --name metroa-backend --gpus all -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  YOUR_USERNAME/metroa-backend:latest
```

**Future deployments:** Just `docker pull` and run - no rebuild needed!

---

## 🔧 Troubleshooting

### Build Fails

```bash
# Check disk space (need 20+ GB)
df -h /workspace

# Clean up Docker
docker system prune -a -f

# Check logs
cat docker-build.log

# Try again with verbose output
docker build --progress=plain -t metroa-backend:latest . 2>&1 | tee build.log
```

### Container Won't Start

```bash
# Check Docker daemon
docker info

# If not running:
pkill dockerd
sleep 2
dockerd > /var/log/dockerd.log 2>&1 &
sleep 5

# Check for port conflicts
lsof -i:8888

# Remove old containers
docker rm -f metroa-backend

# Try starting again
bash README/scripts/run-docker-runpod.sh
```

### Backend Not Responding

```bash
# Check if container is running
docker ps --filter name=metroa-backend

# Check logs for errors
docker logs metroa-backend --tail 100

# Check inside container
docker exec metroa-backend curl http://localhost:8888/health

# Restart container
docker restart metroa-backend
sleep 15
curl http://localhost:8888/health
```

### GPU Not Working

```bash
# Check GPU available to Docker
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi

# Check container has GPU access
docker exec metroa-backend nvidia-smi

# Rebuild with GPU support
docker build --build-arg CUDA_ENABLED=ON -t metroa-backend:latest .
```

---

## 🔄 Update Workflow

When you update the code:

```bash
cd /workspace/metroa-demo

# 1. Pull latest code
git pull origin main

# 2. Rebuild Docker image
docker build -t metroa-backend:latest .

# 3. Restart container
docker stop metroa-backend
docker rm metroa-backend
bash README/scripts/run-docker-runpod.sh
```

**Or use the build script:**
```bash
bash README/scripts/build-docker-runpod.sh
bash README/scripts/run-docker-runpod.sh
```

---

## 📈 Performance Optimization

### Multi-Stage Build (Current)

Our Dockerfile uses multi-stage builds:
- Stage 1: Build COLMAP
- Stage 2: Build OpenMVS  
- Stage 3: Final production image

Only the final stage is kept, reducing image size by ~50%.

### Build Cache

After first build, subsequent builds are faster:
- Changed Python code: ~2 minutes
- Changed requirements.txt: ~5 minutes
- Changed Dockerfile: ~30 minutes

### Runtime Performance

Container runs with:
- `--gpus all` - Full GPU access
- `--restart unless-stopped` - Auto-restart on failure
- Volume mount for persistent data

---

## 🎯 Production Deployment Checklist

- [ ] Docker image built: `docker images | grep metroa-backend`
- [ ] Container running: `docker ps | grep metroa-backend`
- [ ] Health check passing: `curl http://localhost:8888/health`
- [ ] GPU accessible: `docker exec metroa-backend nvidia-smi`
- [ ] COLMAP working: `docker exec metroa-backend colmap --version`
- [ ] Data directory mounted: `docker exec metroa-backend ls /workspace/data`
- [ ] Auto-restart enabled: `docker inspect metroa-backend | grep RestartPolicy`
- [ ] Logs healthy: `docker logs metroa-backend --tail 20`

---

## 📞 Quick Reference

### Build Commands
```bash
# Build image
bash README/scripts/build-docker-runpod.sh

# Or manually
docker build -t metroa-backend:latest .
```

### Run Commands
```bash
# Run container
bash README/scripts/run-docker-runpod.sh

# Or manually
docker run -d --name metroa-backend --gpus all -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend:latest
```

### Test Commands
```bash
# Health check
curl http://localhost:8888/health

# Container status
docker ps --filter name=metroa-backend

# View logs
docker logs metroa-backend --tail 50
```

### Management Commands
```bash
# Stop
docker stop metroa-backend

# Start
docker start metroa-backend

# Restart
docker restart metroa-backend

# Remove
docker rm -f metroa-backend
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs:** `docker logs metroa-backend --tail 100`
2. **Run diagnostics:** `bash README/scripts/diagnose-crash.sh`
3. **Read troubleshooting:** `cat README/troubleshooting/DIAGNOSE_BACKEND_CRASH.md`
4. **Rebuild clean:** `docker system prune -a` then rebuild

---

**Next:** After Docker is running, deploy frontend with:
```bash
cd ~/Desktop/metroa-demo
vercel --prod
```


