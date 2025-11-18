# 🐳 Docker Build Commands - Quick Reference

## 🚀 ONE-LINE BUILD COMMAND

### On RunPod:

```bash
cd /workspace/metroa-demo && bash README/scripts/build-docker-production.sh
```

### On Local Mac:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo && bash README/scripts/build-docker-production.sh
```

---

## 📋 What the Script Does

1. ✅ **Checks prerequisites** (Docker, disk space, GPU)
2. ✅ **Cleans old containers** (if any)
3. ✅ **Builds Docker image** (30-45 minutes first time)
   - Builds COLMAP 3.10 with CUDA support
   - Builds OpenMVS v2.2.0
   - Installs Python dependencies
4. ✅ **Tests the image** (COLMAP, OpenMVS, Python packages)
5. ✅ **Starts the container** (automatically)
6. ✅ **Tests backend health** (curl endpoint)
7. ✅ **Provides next steps** (logs, commands, etc.)

**Total time:** 30-45 minutes (one-time)  
**Result:** Production-ready Docker container running on port 8888

---

## 🎯 Manual Docker Commands (If Script Fails)

### Build Image

```bash
cd /workspace/metroa-demo

# Start Docker (RunPod only)
dockerd > /dev/null 2>&1 &
sleep 3

# Build image (30-45 min)
docker build -t metroa-backend:latest .
```

### Run Container

```bash
# With GPU (RunPod)
docker run -d \
  --name metroa-backend \
  --gpus all \
  -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend:latest

# Without GPU (Mac)
docker run -d \
  --name metroa-backend \
  -p 8888:8888 \
  -v $(pwd)/data:/workspace/data \
  metroa-backend:latest
```

### Test Container

```bash
# Wait for startup
sleep 15

# Test health endpoint
curl http://localhost:8888/health

# Should return:
# {"status":"healthy","message":"Server is running","gpu_available":true}
```

---

## 🔧 Docker Management Commands

### View Logs

```bash
# Follow logs (Ctrl+C to exit)
docker logs -f metroa-backend

# Last 50 lines
docker logs --tail 50 metroa-backend
```

### Container Control

```bash
# Stop container
docker stop metroa-backend

# Start stopped container
docker start metroa-backend

# Restart container
docker restart metroa-backend

# Remove container
docker rm -f metroa-backend
```

### Image Management

```bash
# List images
docker images

# Remove image (will need to rebuild)
docker rmi metroa-backend:latest

# Check image size
docker images metroa-backend:latest --format "{{.Size}}"
```

### Debugging

```bash
# Enter running container
docker exec -it metroa-backend bash

# Run command in container
docker exec metroa-backend colmap --version

# Check container stats
docker stats metroa-backend

# Inspect container
docker inspect metroa-backend
```

---

## 🌐 Push to Docker Hub (Optional)

If you want to reuse the image without rebuilding:

```bash
# 1. Login to Docker Hub
docker login

# 2. Tag image
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest

# 3. Push to Docker Hub
docker push YOUR_USERNAME/metroa-backend:latest

# 4. Pull on another machine (instant!)
docker pull YOUR_USERNAME/metroa-backend:latest
docker run -d --gpus all -p 8888:8888 YOUR_USERNAME/metroa-backend:latest
```

---

## ⏱️ Build Time Breakdown

| Stage | Time | Description |
|-------|------|-------------|
| Base Dependencies | 5 min | System packages |
| COLMAP Build | 20-25 min | GPU-enabled COLMAP from source |
| OpenMVS Build | 10-15 min | Mesh generation tools |
| Final Image | 2 min | Python deps + app code |
| **Total** | **35-45 min** | **First build only** |

**Subsequent builds:** ~2-5 minutes (uses Docker cache)

---

## 💾 Disk Space Requirements

- **Build:** ~15-20 GB temporary
- **Final Image:** ~8-12 GB
- **Runtime:** +2-5 GB per reconstruction

**Total recommended:** 30 GB free space

---

## 🔍 Verification Checklist

After build completes, verify:

```bash
# 1. Container is running
docker ps | grep metroa-backend

# 2. COLMAP is installed
docker exec metroa-backend colmap --version

# 3. Backend responds
curl http://localhost:8888/health

# 4. GPU is accessible (RunPod only)
docker exec metroa-backend nvidia-smi
```

All should return successfully.

---

## 🆘 Troubleshooting

### Build fails with "no space left on device"

```bash
# Clean Docker cache
docker system prune -a -f

# Check space
df -h
```

### Build fails at COLMAP stage

```bash
# Check build logs
cat docker-build.log | grep -i error

# Try building with more verbose output
docker build --progress=plain -t metroa-backend:latest .
```

### Container starts but backend doesn't respond

```bash
# Check logs for errors
docker logs metroa-backend

# Common issues:
# - Port 8888 already in use: lsof -i:8888
# - Missing dependencies: docker exec metroa-backend pip list
# - Permission issues: docker logs metroa-backend | grep Permission
```

### GPU not accessible in container

```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi

# If fails, install NVIDIA container toolkit:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

---

## 📊 Expected Output

When script completes successfully:

```
============================================
✅ BUILD COMPLETE!
============================================

📦 Image: metroa-backend:latest
🐳 Container: metroa-backend
🌐 Port: 8888
⏱️  Build time: 38m 42s

🎯 Useful Commands:

View logs:
  docker logs -f metroa-backend

Test health endpoint:
  curl http://localhost:8888/health

============================================
🎉 SETUP COMPLETE!
============================================

Your Metroa backend is now running in Docker with:
  ✅ COLMAP 3.10
  ✅ OpenMVS v2.2.0
  ✅ Open3D 0.19.0
  ✅ Python 3.12 + FastAPI
  ✅ GPU Acceleration
```

---

## 🎯 Quick Start Summary

**First Time (RunPod):**
```bash
cd /workspace/metroa-demo
bash README/scripts/build-docker-production.sh
# Wait 35-45 minutes
# Backend will be running on port 8888
```

**Subsequent Restarts:**
```bash
docker start metroa-backend
# Instant startup, no rebuild needed
```

**Frontend Deploy:**
```bash
# On your Mac
cd /Users/marco.aurelio/Desktop/metroa-demo
vercel --prod
```

---

## 📞 Support

If build fails, check:
1. `docker-build.log` for detailed error messages
2. Disk space: `df -h`
3. Docker daemon: `docker info`
4. README/troubleshooting/ for specific error fixes

---

**The script handles everything automatically - just run it and wait!** 🚀


