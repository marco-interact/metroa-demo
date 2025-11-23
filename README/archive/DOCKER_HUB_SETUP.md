# 🐳 Docker Hub Setup Guide

## ❌ Error: "push access denied"

This means the repository doesn't exist on Docker Hub yet.

---

## ✅ **Solution: Create Repository on Docker Hub**

### **Step 1: Go to Docker Hub**

Visit: https://hub.docker.com/

**Login** with your Docker Hub credentials

### **Step 2: Create Repository**

1. Click **Repositories** (top menu)
2. Click **Create Repository** button
3. Fill in:
   - **Repository Name:** `metroa-backend`
   - **Visibility:** Public (or Private if you have a paid plan)
   - **Description:** (optional) "Metroa 3D reconstruction backend with COLMAP"
4. Click **Create**

Your repository will be: `YOUR_USERNAME/metroa-backend`

---

## 🚀 **Step 3: Push Image**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Verify you're logged in
docker login

# Tag image with YOUR Docker Hub username
docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest

# Push to Docker Hub
docker push YOUR_USERNAME/metroa-backend:latest
```

**Example (replace `marcointeract` with YOUR username):**
```bash
docker login
# Username: marcointeract
# Password: (your Docker Hub password)
# Login Succeeded

docker tag metroa-backend:fast marcointeract/metroa-backend:latest
docker push marcointeract/metroa-backend:latest
```

---

## 📊 **What to Expect**

```bash
docker push marcointeract/metroa-backend:latest

The push refers to repository [docker.io/marcointeract/metroa-backend]
a1b2c3d4e5f6: Pushing [==============>                ] 1.5GB/5GB
...
latest: digest: sha256:abc123... size: 1234
```

**Time:** 5-15 minutes depending on your upload speed

---

## 🔑 **Find Your Docker Hub Username**

1. Go to https://hub.docker.com/
2. Click your profile icon (top right)
3. Your username is shown there

**Or check locally:**
```bash
docker info | grep Username
```

---

## ⚠️ **Common Issues**

### **Issue 1: "denied: requested access to the resource is denied"**
- **Cause:** Repository doesn't exist
- **Fix:** Create repository on Docker Hub (Step 2 above)

### **Issue 2: "unauthorized: authentication required"**
- **Cause:** Not logged in
- **Fix:** Run `docker login` again

### **Issue 3: "denied: insufficient_scope"**
- **Cause:** Repository name doesn't match your username
- **Fix:** Make sure you use YOUR_USERNAME/metroa-backend

---

## 📝 **Quick Checklist**

- [ ] Have Docker Hub account (https://hub.docker.com/signup)
- [ ] Logged in: `docker login`
- [ ] Created repository `metroa-backend` on Docker Hub
- [ ] Tagged image: `docker tag metroa-backend:fast YOUR_USERNAME/metroa-backend:latest`
- [ ] Pushed image: `docker push YOUR_USERNAME/metroa-backend:latest`

---

## 🎯 **After Push Succeeds**

Your image will be available at:
```
https://hub.docker.com/r/YOUR_USERNAME/metroa-backend
```

Then you can use it on RunPod:
```
Container Image: YOUR_USERNAME/metroa-backend:latest
```

---

## 🆘 **Still Having Issues?**

### **Verify local image exists:**
```bash
docker images | grep metroa-backend
# Should show: metroa-backend   fast   ...
```

### **Check Docker Hub username:**
```bash
docker info | grep Username
```

### **Try creating a test repository:**
1. Go to https://hub.docker.com/
2. Create repository named `test`
3. Push: `docker tag metroa-backend:fast YOUR_USERNAME/test:latest`
4. Push: `docker push YOUR_USERNAME/test:latest`

---

## 📚 **Docker Hub Documentation**

- Create repository: https://docs.docker.com/docker-hub/repos/create/
- Push images: https://docs.docker.com/docker-hub/repos/#pushing-a-docker-container-image-to-docker-hub

---

**Next:** Once push succeeds, go back to [DEPLOY_NOW.md](DEPLOY_NOW.md) Step 2!

