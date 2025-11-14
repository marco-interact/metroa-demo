# 🐳 Docker Build Instructions

**How to build the Metroa backend GPU image**

---

## 🍎 Building on macOS (Local Development)

### Prerequisites

1. **Docker Desktop** must be installed and running
   - Download: https://www.docker.com/products/docker-desktop/
   - Start Docker Desktop before building

2. **Check Docker is running:**
   ```bash
   docker ps
   # Should not show an error
   ```

### Build Command

```bash
# Start Docker Desktop first, then:
make build
# or
./docker-build.sh
```

**Note:** The image will build successfully, but GPU features won't work on macOS. This is fine for testing the build process.

---

## 🐧 Building on Linux (with GPU)

### Prerequisites

1. **NVIDIA Docker runtime** installed
   ```bash
   # Check if installed
   docker info | grep nvidia
   ```

2. **NVIDIA drivers** installed
   ```bash
   nvidia-smi
   ```

### Build Command

```bash
make build
# or
./docker-build.sh
```

**GPU features will work** when running the container with `--gpus all`.

---

## ☁️ Building on RunPod (Recommended)

**Best option for production builds with GPU support**

### Option 1: Build in RunPod Container

1. **SSH into your RunPod pod:**
   ```bash
   ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519
   ```

2. **Clone repo and build:**
   ```bash
   cd /workspace
   git clone https://github.com/marco-interact/metroa-demo.git
   cd metroa-demo
   
   # Install Docker (if not already installed)
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Build image
   make build
   ```

3. **Tag and push to registry:**
   ```bash
   # Tag for your registry
   docker tag metroa-backend:latest your-registry/metroa-backend:v1.0.0
   
   # Push
   docker push your-registry/metroa-backend:v1.0.0
   ```

### Option 2: Use RunPod's Build Service

1. Go to RunPod Dashboard
2. Use their container build service
3. Point to your Dockerfile
4. Build with GPU support

---

## 🚀 Quick Start (macOS)

**If Docker Desktop is not running:**

1. **Start Docker Desktop:**
   - Open Docker Desktop app
   - Wait for it to start (whale icon in menu bar)
   - Verify: `docker ps` should work

2. **Then build:**
   ```bash
   make build
   ```

**Expected output:**
```
🔨 Building metroa-backend:latest...
📦 Building Docker image...
⏱  This will take 30-45 minutes...
[build output...]
✅ Build successful!
```

---

## 🔍 Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Solution:** Start Docker Desktop (macOS) or Docker service (Linux)

**macOS:**
```bash
# Open Docker Desktop app
open -a Docker
```

**Linux:**
```bash
sudo systemctl start docker
```

### Error: "NVIDIA Docker runtime not detected"

**On macOS:** This is expected - GPU won't work locally, but build will succeed

**On Linux:** Install NVIDIA Docker runtime:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Build Fails: Out of Memory

**Solution:** Increase Docker Desktop memory limit (macOS) or add swap (Linux)

**macOS:**
- Docker Desktop → Settings → Resources → Memory
- Increase to at least 8GB

**Linux:**
```bash
# Add swap if needed
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## ✅ Verify Build

After build completes:

```bash
# Check image exists
docker images metroa-backend:latest

# Test tools (without GPU)
docker run --rm metroa-backend:latest \
  sh -c "colmap --help | head -3 && \
         DensifyPointCloud --help | head -3 && \
         python3.12 -c 'import open3d; print(open3d.__version__)'"
```

---

## 📤 Push to Registry

After successful build:

```bash
# Tag for your registry
docker tag metroa-backend:latest your-registry/metroa-backend:v1.0.0

# Login to registry
docker login your-registry.com

# Push
docker push your-registry/metroa-backend:v1.0.0
```

---

## 🎯 Recommended Workflow

**For Production:**

1. **Build on RunPod** (has GPU, faster builds)
2. **Push to Docker Hub or private registry**
3. **Use in RunPod templates**

**For Local Testing:**

1. **Build on macOS** (Docker Desktop)
2. **Test basic functionality** (no GPU)
3. **Deploy to RunPod** for GPU testing

---

## ⏱️ Build Times

| Platform | Time | GPU Support |
|----------|------|-------------|
| macOS (M1/M2) | ~45-60 min | ❌ No |
| macOS (Intel) | ~40-50 min | ❌ No |
| Linux (CPU) | ~35-45 min | ❌ No |
| Linux (GPU) | ~30-40 min | ✅ Yes |
| RunPod (GPU) | ~25-35 min | ✅ Yes |

---

**Next Steps:** Start Docker Desktop, then run `make build` again!

