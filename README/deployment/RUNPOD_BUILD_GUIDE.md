# 🚀 RunPod Build Guide - Workaround for Local Disk Issues

Your local disk is 98% full, causing Docker I/O errors. Here are two solutions:

---

## ✅ **OPTION 1: Build on RunPod (FASTEST)**

Build the Docker image directly on your RunPod instance where there's plenty of disk space.

### Steps:

1. **SSH into your RunPod instance:**
   ```bash
   ssh root@YOUR_POD_IP -p YOUR_SSH_PORT -i ~/.ssh/id_ed25519
   ```
   
   Find your SSH details at: https://www.runpod.io/console/pods

2. **Install required tools (if not already installed):**
   ```bash
   apt-get update && apt-get install -y git docker.io
   ```

3. **Upload your code** (choose one method):
   
   **Method A: Via Git (if you have a GitHub repo):**
   ```bash
   cd /workspace
   git clone https://github.com/YOUR_USERNAME/metroa-demo.git
   cd metroa-demo
   ```
   
   **Method B: Via SCP (from your Mac):**
   ```bash
   # On your local Mac:
   scp -P YOUR_SSH_PORT -i ~/.ssh/id_ed25519 -r /Users/marco.aurelio/Desktop/metroa-demo root@YOUR_POD_IP:/workspace/
   ```

4. **Build on RunPod:**
   ```bash
   cd /workspace/metroa-demo
   docker build --platform=linux/amd64 -t macoaurelio/metroa-backend:latest .
   ```

5. **Login and Push to Docker Hub:**
   ```bash
   docker login
   docker push macoaurelio/metroa-backend:latest
   ```

6. **Pull the image in your pod:**
   ```bash
   docker pull macoaurelio/metroa-backend:latest
   docker run --gpus all -p 8888:8888 -v /workspace/data:/workspace/data macoaurelio/metroa-backend:latest
   ```

---

## 🔧 **OPTION 2: Fix Local Docker (Slower)**

Free up disk space on your Mac and rebuild locally.

### Steps:

1. **Restart Docker Desktop** (fixes corruption):
   - Open Docker Desktop
   - Click "Troubleshoot" → "Restart Docker"

2. **Free up disk space** (need at least 30GB free):
   ```bash
   # Remove Docker build cache
   docker builder prune --all --force
   
   # Remove unused Docker images
   docker image prune -a --force
   
   # Remove unused Docker volumes
   docker volume prune --force
   
   # Check available space
   df -h /
   ```

3. **Clean up other files** (if still low on space):
   - Empty Trash
   - Delete old Xcode simulators: `xcrun simctl delete unavailable`
   - Delete Homebrew cache: `brew cleanup`
   - Delete npm cache: `npm cache clean --force`

4. **Rebuild:**
   ```bash
   cd /Users/marco.aurelio/Desktop/metroa-demo
   ./deploy.sh
   ```

---

## 📋 **Your RunPod Info**

- **Pod ID:** vgc2jw8pa9dk4t
- **Console:** https://www.runpod.io/console/pods
- **SSH Command:** Check RunPod console for your specific SSH command

---

## 🎯 **Recommendation**

**Use Option 1 (Build on RunPod)** because:
- ✅ No local disk space issues
- ✅ Faster build (RunPod has better CPU/network)
- ✅ Already on the target platform (linux/amd64)
- ✅ No cross-platform compilation issues

---

## 💡 **Alternative: Use Pre-built Image**

If you just want to test quickly, you can use an existing COLMAP+OpenMVS image:

```bash
# On RunPod:
docker pull cdcseacave/openmvs:latest
# Then adapt your code to run in this container
```

---

## Need Help?

1. Check RunPod SSH access: https://docs.runpod.io/pods/configuration/expose-ports
2. Docker build failing? Check: `docker system df` and ensure >30GB free
3. Still stuck? Consider building in a cloud CI/CD (GitHub Actions, GitLab CI)

