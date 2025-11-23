# 🐳 RunPod Docker Guide - Official Workflow

> Based on [RunPod's Docker Documentation](https://docs.runpod.io/tutorials/introduction/containers/docker-commands)

## 🎯 **How RunPod Works with Docker**

RunPod uses **BYOC (Bring Your Own Container)**:

1. ✅ Build Docker image **locally** (on your Mac)
2. ✅ Push to **Docker Hub** (or registry)
3. ✅ RunPod **pulls and runs** your image
4. ✅ No Docker installation needed inside RunPod

**You do NOT run `docker build` on RunPod!**

---

## 🚀 **Complete Workflow**

### **Step 1: Build Docker Image Locally**

On your **Mac** with Docker Desktop:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# IMPORTANT: Use --platform=linux/amd64 for RunPod compatibility
docker build --platform=linux/amd64 \
  -t metroa-backend:latest \
  -f Dockerfile.fast \
  .
```

**Why `--platform=linux/amd64`?**
Per [RunPod docs](https://docs.runpod.io/tutorials/introduction/containers/docker-commands), this ensures compatibility with RunPod's infrastructure.

---

### **Step 2: Test Locally**

```bash
# Run on your Mac
docker run -d --name metroa-test -p 8888:8888 metroa-backend:latest

# Test
curl http://localhost:8888/health

# Clean up
docker stop metroa-test
docker rm metroa-test
```

---

### **Step 3: Push to Docker Hub**

```bash
# Login (one time)
docker login

# Tag for Docker Hub
docker tag metroa-backend:latest YOUR_DOCKERHUB_USERNAME/metroa-backend:latest

# Push
docker push YOUR_DOCKERHUB_USERNAME/metroa-backend:latest
```

Your image is now available at: `YOUR_DOCKERHUB_USERNAME/metroa-backend:latest`

---

### **Step 4: Deploy on RunPod**

#### Option A: Using RunPod Web UI

1. Go to **RunPod Console** → **Pods**
2. Click **Deploy**
3. Choose **GPU** (RTX 4090 recommended)
4. Under **Container Image**, enter:
   ```
   YOUR_DOCKERHUB_USERNAME/metroa-backend:latest
   ```
5. **Expose HTTP Ports**: `8888`
6. **Container Disk**: 50 GB
7. Click **Deploy**

#### Option B: Using RunPod Template

Create a template with:

```yaml
Name: Metroa Backend
Container Image: YOUR_DOCKERHUB_USERNAME/metroa-backend:latest
Docker Command: (leave empty)

GPU: RTX 4090 (or any CUDA GPU)
Container Disk: 50 GB
Volume Disk: 50 GB (optional)

Expose HTTP Ports: 8888

Environment Variables:
  PYTHONUNBUFFERED: "1"
  CUDA_VISIBLE_DEVICES: "0"
```

---

## 📦 **Build Options**

### **Fast Build (Recommended) - 5-10 minutes**

Uses pre-compiled COLMAP:

```bash
docker build --platform=linux/amd64 \
  -t metroa-backend:latest \
  -f Dockerfile.fast \
  .
```

**Features:**
- ✅ COLMAP 3.x (GPU-enabled)
- ✅ All core features
- ✅ 4-6 GB image size
- ✅ Perfect for production

### **Production Build - 30-45 minutes**

Compiles COLMAP from source:

```bash
docker build --platform=linux/amd64 \
  -t metroa-backend:latest \
  -f Dockerfile \
  .
```

**Features:**
- ✅ COLMAP 3.10 (latest, built from source)
- ✅ OpenMVS for ultra-dense point clouds
- ✅ RTX 4090 optimized
- ✅ Maximum performance
- ⚠️ 8-12 GB image size

**Both work perfectly!** Choose based on your needs.

---

## 🔧 **Complete Build Script**

Use the provided script:

```bash
bash docker-build-local.sh
```

This script:
1. Checks Docker is running
2. Lets you choose fast/full build
3. Builds with correct platform flag
4. Tests the image
5. Shows push commands

---

## 📋 **RunPod Access**

After deployment, access your backend:

### Find Your Pod ID:
In RunPod console, copy your Pod ID (looks like: `abc123def456`)

### Access URLs:
- **RunPod Proxy:** `https://abc123def456-8888.proxy.runpod.net`
- **SSH into pod:** Use RunPod's SSH command

### Test Backend:
```bash
curl https://YOUR-POD-ID-8888.proxy.runpod.net/health
```

---

## 🔄 **Update Workflow**

When you make code changes:

```bash
# 1. Rebuild locally
docker build --platform=linux/amd64 -t metroa-backend:latest -f Dockerfile.fast .

# 2. Push to Docker Hub
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest

# 3. Restart RunPod pod
# In RunPod console: Stop → Start your pod
# Or create new pod with updated image
```

RunPod will pull the latest version automatically.

---

## 📊 **Dockerfile Comparison**

| File | Build Time | Size | Best For |
|------|-----------|------|----------|
| **Dockerfile.fast** | 5-10 min | 4-6 GB | Production, Development |
| **Dockerfile** | 30-45 min | 8-12 GB | Maximum performance |

**Recommendation:** Use `Dockerfile.fast` - it has everything you need!

---

## ✅ **Commands Cheat Sheet**

### Build (on Mac):
```bash
# Fast build
docker build --platform=linux/amd64 -f Dockerfile.fast -t metroa-backend:latest .

# Full build
docker build --platform=linux/amd64 -f Dockerfile -t metroa-backend:latest .
```

### Push to Docker Hub:
```bash
docker login
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest
```

### Test Locally:
```bash
docker run -d --name test -p 8888:8888 metroa-backend:latest
curl http://localhost:8888/health
docker stop test && docker rm test
```

### View Logs (on RunPod):
```bash
# SSH into RunPod pod, then:
docker logs $(docker ps -q)
```

---

## 🎯 **Key Points**

1. ✅ **Build locally** with `--platform=linux/amd64`
2. ✅ **Push to Docker Hub**
3. ✅ **Deploy on RunPod** via template or UI
4. ✅ **RunPod handles everything** (no docker commands inside pod)
5. ✅ **Update:** Rebuild → Push → Restart pod

---

## 🆘 **Troubleshooting**

### "Docker is not running"
**Solution:** Start Docker Desktop on your Mac

### "Platform mismatch" error on RunPod
**Solution:** Rebuild with `--platform=linux/amd64` flag

### Image too large
**Solution:** Use `Dockerfile.fast` instead

### Backend not responding on RunPod
**Solution:** Check RunPod logs and ensure port 8888 is exposed

### Can't push to Docker Hub
```bash
# Login first
docker login

# Create account at hub.docker.com if needed
```

---

## 📚 **Official References**

- [RunPod Docker Commands](https://docs.runpod.io/tutorials/introduction/containers/docker-commands)
- [RunPod Container Deployment](https://docs.runpod.io/tutorials/introduction/containers)
- [Docker Hub](https://hub.docker.com)

---

## 🎉 **Summary**

**The CORRECT way to use Docker with RunPod:**

1. Build image on your Mac: ✅
2. Push to Docker Hub: ✅
3. Deploy on RunPod: ✅
4. No Docker inside RunPod: ✅

**NOT this way:**
- ❌ Building Docker inside RunPod
- ❌ Installing Docker on RunPod
- ❌ Docker-in-Docker

---

## 🚀 **Your Commands**

```bash
# On your Mac:
cd /Users/marco.aurelio/Desktop/metroa-demo
bash docker-build-local.sh
# Follow prompts to build and test

# Push to Docker Hub:
docker login
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest

# On RunPod:
# Use YOUR_USERNAME/metroa-backend:latest in template
# Deploy → Done!
```

---

**Need help?** Check:
- `docker-build-local.sh` - Automated build script
- `DOCKER_QUICKSTART.md` - Quick reference
- `Dockerfile.fast` - Fast build Dockerfile
- `Dockerfile` - Production build Dockerfile

