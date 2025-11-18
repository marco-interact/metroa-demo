# 🚀 Deploy Metroa - Complete Guide

**Pod Details:**
- Pod ID: `b444omwmnc2n3g`
- Backend URL: `https://b444omwmnc2n3g-8888.proxy.runpod.net`
- SSH: `ssh root@203.57.40.153 -p 10226 -i ~/.ssh/id_ed25519`
- Port: 8888
- Volume: None (BYOC - image contains everything!)

---

## 📦 **Step 1: Push Docker Image to Docker Hub**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Login to Docker Hub
docker login

# Tag the image (replace YOUR_USERNAME with your Docker Hub username)
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest

# Push to Docker Hub
docker push YOUR_USERNAME/metroa-backend:latest
```

**Example:**
```bash
docker login
# Username: marcointeract
# Password: (enter your password)

docker tag metroa-backend:fast marcointeract/metroa-backend:latest
docker push marcointeract/metroa-backend:latest
```

---

## 🎮 **Step 2: Configure RunPod Pod**

### **Option A: Via RunPod Web UI (Recommended)**

1. Go to [RunPod Console](https://runpod.io)
2. Find pod `b444omwmnc2n3g`
3. **Stop the pod** (if running)
4. Click **Edit**
5. Update **Container Image** to: `YOUR_USERNAME/metroa-backend:latest`
6. Ensure **Expose HTTP Ports** is: `8888`
7. Click **Save**
8. **Start the pod**

### **Option B: Via RunPod API (Advanced)**

If you need to use the API, update the template/pod with your image.

---

## 🧪 **Step 3: Test Backend**

Wait 30-60 seconds for the container to start, then test:

```bash
# Test health endpoint
curl https://b444omwmnc2n3g-8888.proxy.runpod.net/health

# Should return:
{
  "status": "healthy",
  "gpu_available": true,
  "message": "Server is running"
}
```

**If it doesn't work:**
```bash
# SSH into pod
ssh root@203.57.40.153 -p 10226 -i ~/.ssh/id_ed25519

# Check if container is running
docker ps

# Check logs
docker logs $(docker ps -q)

# Check if backend is listening
curl http://localhost:8888/health
```

---

## 🌐 **Step 4: Update Frontend & Deploy**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Update backend URL
echo 'NEXT_PUBLIC_API_URL=https://b444omwmnc2n3g-8888.proxy.runpod.net' > .env.production

# Deploy to Vercel
vercel --prod
```

---

## ✅ **Step 5: Verify Everything Works**

1. **Test backend directly:**
   - https://b444omwmnc2n3g-8888.proxy.runpod.net/health
   - https://b444omwmnc2n3g-8888.proxy.runpod.net/docs (API docs)

2. **Test frontend:**
   - Visit your Vercel URL
   - Try uploading a video
   - Check if processing starts

---

## 🔄 **Update Workflow (For Future Changes)**

When you make code changes:

```bash
# 1. Rebuild Docker image
bash docker-build-local.sh
# Select: 1 (Fast Build)

# 2. Push to Docker Hub
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest

# 3. Restart RunPod pod
# In RunPod console: Stop → Start pod
# Or via SSH:
ssh root@203.57.40.153 -p 10226 -i ~/.ssh/id_ed25519
docker pull YOUR_USERNAME/metroa-backend:latest
docker stop $(docker ps -q)
docker run -d -p 8888:8888 YOUR_USERNAME/metroa-backend:latest

# 4. Update frontend (if needed)
vercel --prod
```

---

## 🆘 **Troubleshooting**

### **Backend not responding:**
```bash
# SSH into pod
ssh root@203.57.40.153 -p 10226 -i ~/.ssh/id_ed25519

# Check container status
docker ps
docker logs $(docker ps -q)

# Restart container
docker stop $(docker ps -q)
docker run -d -p 8888:8888 YOUR_USERNAME/metroa-backend:latest
```

### **"Image not found" error:**
- Make sure you pushed to Docker Hub
- Check image name matches exactly
- Try: `docker pull YOUR_USERNAME/metroa-backend:latest` from your Mac

### **Frontend can't connect:**
- Check `.env.production` has correct URL
- Redeploy frontend: `vercel --prod`
- Check CORS settings (should be fine)

---

## 📊 **Pod Specifications**

- **Pod ID:** b444omwmnc2n3g
- **GPU:** RTX 4090 (assumed)
- **Container Disk:** 50 GB (temporary, no volume)
- **Image:** YOUR_USERNAME/metroa-backend:latest
- **Port:** 8888
- **Backend URL:** https://b444omwmnc2n3g-8888.proxy.runpod.net

---

## 🎯 **Summary**

```bash
# 1. Push image
docker login
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest
docker push YOUR_USERNAME/metroa-backend:latest

# 2. Update RunPod pod to use your image
# (via web UI)

# 3. Test backend
curl https://b444omwmnc2n3g-8888.proxy.runpod.net/health

# 4. Deploy frontend
echo 'NEXT_PUBLIC_API_URL=https://b444omwmnc2n3g-8888.proxy.runpod.net' > .env.production
vercel --prod

# Done! 🎉
```

---

**Ready?** Start with Step 1! 🚀

