# 🐳 Proper Docker Setup for RunPod

## 🎯 **The Right Approach**

RunPod **runs Docker containers** - you don't build/run Docker inside the pod.

**Correct workflow:**
1. Build Docker image (locally or on RunPod)
2. Push to Docker Hub
3. Use that image in RunPod template
4. RunPod runs it for you

---

## 🚀 **Option 1: Use Pre-Built Image (Fastest)**

### On RunPod:

```bash
# Just run the pre-built image
docker pull YOUR_DOCKERHUB/metroa-backend:latest
```

### Or use this in RunPod Template:
- **Container Image:** `YOUR_DOCKERHUB/metroa-backend:latest`
- **Container Disk:** 50 GB
- **Expose Ports:** 8888
- **Environment:** Leave empty or set backend vars

---

## 🏗️ **Option 2: Build on Local Machine (Recommended)**

### On your Mac with Docker Desktop:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Build for production (30-45 min one time)
docker build -t metroa-backend:latest .

# Or build fast version (5-10 min)
docker build -f Dockerfile.fast -t metroa-backend:latest .

# Test locally
docker run -d --name test -p 8888:8888 metroa-backend:latest
curl http://localhost:8888/health

# Tag for Docker Hub
docker tag metroa-backend:latest YOUR_DOCKERHUB_USERNAME/metroa-backend:latest

# Push to Docker Hub
docker login
docker push YOUR_DOCKERHUB_USERNAME/metroa-backend:latest
```

### Then on RunPod:
Use Docker Hub image in your template!

---

## 🔨 **Option 3: Build on RunPod (If no local Docker)**

This is where you ran into issues. Here's the CORRECT way:

```bash
cd /workspace/metroa-demo

# Method A: Use RunPod's Docker (if available)
# Check if docker command exists:
which docker

# If yes:
docker build -f Dockerfile.fast -t metroa-backend:latest .

# Method B: Build locally in workspace (no Docker needed)
# Install build dependencies
apt-get update && apt-get install -y colmap ffmpeg libgl1-mesa-glx libglib2.0-0 libsm6 libxext6
pip install -r requirements.txt

# Then just run:
python main.py
```

---

## 📦 **Optimized Dockerfile (Clean & Fast)**

I'll create a streamlined Dockerfile that:
- ✅ Uses pre-compiled COLMAP (5-10 min build)
- ✅ Minimal layers for smaller image
- ✅ GPU-enabled
- ✅ Production-ready

---

## 🎯 **Recommended Workflow**

### **For Production (Best Performance):**

1. **Build locally** (your Mac with Docker Desktop):
   ```bash
   docker build -t YOUR_USERNAME/metroa-backend:latest .
   docker push YOUR_USERNAME/metroa-backend:latest
   ```

2. **Use in RunPod Template:**
   - Container Image: `YOUR_USERNAME/metroa-backend:latest`
   - Expose HTTP Ports: 8888
   - Done!

### **For Quick Testing:**

1. **On RunPod:**
   ```bash
   cd /workspace/metroa-demo
   apt-get update && apt-get install -y colmap ffmpeg
   pip install -r requirements.txt
   python main.py
   ```

---

## ⚙️ **RunPod Template Settings**

```yaml
Container Image: your-dockerhub/metroa-backend:latest
Container Disk: 50 GB
Expose HTTP Ports: 8888
Docker Command: (leave empty - uses CMD from Dockerfile)
Environment Variables:
  PYTHONUNBUFFERED: 1
  CUDA_VISIBLE_DEVICES: 0
```

---

## 🐳 **Docker Hub Publishing**

```bash
# Login
docker login

# Build
docker build -t metroa-backend:latest .

# Tag
docker tag metroa-backend:latest YOUR_USERNAME/metroa-backend:latest

# Push
docker push YOUR_USERNAME/metroa-backend:latest
```

Now anyone can use: `docker pull YOUR_USERNAME/metroa-backend:latest`

---

## ✅ **Key Points**

1. **Don't run Docker inside RunPod's container**
2. **Build image once, use everywhere**
3. **Push to Docker Hub for persistence**
4. **Let RunPod run the container**

---

This is the proper way to use Docker with RunPod!

