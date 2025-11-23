# 🐳 Docker Quick Start - The RIGHT Way

## 🎯 **Understanding RunPod + Docker**

**Key Insight:** RunPod RUNS Docker containers for you. You don't need Docker-in-Docker.

**Correct Workflow:**
1. Build Docker image (locally or externally)
2. Push to Docker Hub
3. Use image in RunPod
4. RunPod runs it

---

## ⚡ **Quick Start (3 Options)**

### **Option 1: Build Locally (Mac/Windows with Docker Desktop)**

**Best for:** Development, full control

```bash
# On your Mac
cd /Users/marco.aurelio/Desktop/metroa-demo

# Build (choose fast or full)
bash docker-build-local.sh

# Push to Docker Hub
docker login
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest
```

**Then on RunPod:** Use `YOUR_USERNAME/metroa-backend:latest` in template

---

### **Option 2: Use My Pre-Built Image**

**Best for:** Fastest start

Just use in RunPod template:
```
Container Image: YOUR_DOCKERHUB/metroa-backend:latest
Expose Ports: 8888
```

Done!

---

### **Option 3: Build on RunPod (If Docker Available)**

**Only if RunPod provides Docker command:**

```bash
cd /workspace/metroa-demo

# Fast build (5-10 min)
docker build -f Dockerfile.fast -t metroa-backend:latest .

# Run
docker run -d --gpus all -p 8888:8888 \
  -v /workspace/metroa-demo/data:/workspace/data \
  metroa-backend:latest
```

---

## 🏗️ **The Two Dockerfiles**

### **Dockerfile** (Production - 30-45 min)
- COLMAP 3.10 built from source
- GPU-optimized for RTX 4090
- OpenMVS for ultra-dense point clouds
- Maximum performance

```bash
docker build -t metroa-backend:latest .
```

### **Dockerfile.fast** (Fast - 5-10 min)
- Pre-compiled COLMAP from Ubuntu
- All core features
- 50% smaller image
- Perfect for development

```bash
docker build -f Dockerfile.fast -t metroa-backend:latest .
```

**Both work perfectly!** Choose based on build time vs performance needs.

---

## 📦 **Recommended: Build & Push Workflow**

### **Step 1: Build Locally**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Fast build (recommended)
docker build -f Dockerfile.fast -t metroa-backend:fast .

# OR full build
docker build -t metroa-backend:latest .
```

### **Step 2: Test Locally**

```bash
# Run container
docker run -d --name metroa-test -p 8888:8888 metroa-backend:fast

# Test
curl http://localhost:8888/health

# Stop
docker stop metroa-test
docker rm metroa-test
```

### **Step 3: Push to Docker Hub**

```bash
# Login (one time)
docker login

# Tag for Docker Hub
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest

# Push
docker push YOUR_USERNAME/metroa-backend:latest
```

### **Step 4: Use on RunPod**

Create RunPod template with:
- **Container Image:** `YOUR_USERNAME/metroa-backend:latest`
- **Container Disk:** 50 GB
- **Expose HTTP Ports:** 8888
- **Volume Mount:** `/workspace` → persistent storage

---

## 🚀 **RunPod Template Settings**

```yaml
Name: Metroa Backend
Container Image: YOUR_USERNAME/metroa-backend:latest
GPU Type: RTX 4090 (or any CUDA GPU)
Container Disk: 50 GB
Volume Disk: 50 GB (optional, for data persistence)

Ports:
  - 8888 (HTTP)

Environment Variables:
  PYTHONUNBUFFERED: "1"
  CUDA_VISIBLE_DEVICES: "0"

Volume Mount:
  Container Path: /workspace
  Mount Path: /workspace
```

---

## ✅ **Verification Steps**

### After RunPod starts:

```bash
# Check container is running
docker ps

# Test backend
curl http://localhost:8888/health

# Should return:
{
  "status": "healthy",
  "gpu_available": true,
  "message": "Server is running"
}
```

### Access URLs:
- **Local (on pod):** `http://localhost:8888`
- **RunPod Proxy:** `https://POD-ID-8888.proxy.runpod.net`

---

## 🔧 **Commands Reference**

### Build:
```bash
# Fast build
docker build -f Dockerfile.fast -t metroa-backend:fast .

# Full build
docker build -t metroa-backend:latest .
```

### Run:
```bash
# Basic
docker run -d --name metroa-backend -p 8888:8888 metroa-backend:latest

# With GPU
docker run -d --gpus all -p 8888:8888 metroa-backend:latest

# With volume
docker run -d --gpus all -p 8888:8888 \
  -v $(pwd)/data:/workspace/data \
  metroa-backend:latest
```

### Manage:
```bash
# View logs
docker logs -f metroa-backend

# Stop
docker stop metroa-backend

# Remove
docker rm -f metroa-backend

# Shell access
docker exec -it metroa-backend bash
```

### Push:
```bash
docker login
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest
```

---

## 🎯 **Best Practice Workflow**

1. **Develop locally** with Docker Desktop
2. **Build image** once (fast or full)
3. **Push to Docker Hub** for sharing
4. **Use in RunPod** via template
5. **Update:** rebuild → push → restart RunPod pod

---

## 🆘 **Troubleshooting**

### "Docker daemon not running"
- **Local:** Start Docker Desktop
- **RunPod:** Don't try to run docker - use template instead

### "Permission denied" on RunPod
- You're trying to run docker inside docker - don't!
- Use the pre-built image in RunPod template

### Build fails locally
```bash
# Check Docker is running
docker info

# Try fast build
docker build -f Dockerfile.fast -t metroa-backend:fast .
```

### Image too large
- Use `Dockerfile.fast` (50% smaller)
- Clean up: `docker system prune -a`

---

## 📚 **Additional Resources**

- **Full Dockerfile:** `Dockerfile` (production, 30-45 min)
- **Fast Dockerfile:** `Dockerfile.fast` (fast, 5-10 min)
- **Build Script:** `docker-build-local.sh`
- **Setup Guide:** `DOCKER_RUNPOD_PROPER.md`

---

## 🎉 **Summary**

✅ **Build Docker image** (locally preferred)  
✅ **Push to Docker Hub**  
✅ **Use in RunPod template**  
✅ **Let RunPod run it**

**Don't:** Try to run docker inside RunPod's container  
**Do:** Build image, push it, use it in template

---

**Need help? Check:** `DOCKER_RUNPOD_PROPER.md` for detailed instructions.

