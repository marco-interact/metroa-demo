# 🔄 RunPod Pod Rotation & Deployment Guide

Complete guide for terminating old pods and deploying new ones with the latest Docker image.

---

## 📋 **Quick Steps Overview**

1. ✅ Verify Docker image is built and pushed
2. 🛑 Terminate current pod(s)
3. 🚀 Deploy new pod with latest configuration
4. 🔗 Update frontend connection
5. ✅ Verify deployment

---

## **Step 1: Verify Docker Image is Ready**

Before terminating pods, ensure your Docker image is built and pushed to Docker Hub.

### **✅ Pre-Termination Checklist**

- [ ] Docker image built: `docker images | grep metroa-backend`
- [ ] Docker image pushed: `docker pull macoaurelio/metroa-backend:latest` (should work)
- [ ] Current pod ID saved: `_____________________`
- [ ] Current proxy URL saved: `https://_______________-8888.proxy.runpod.net`
- [ ] GPU type noted: `_____________________`
- [ ] Volume size noted: `_____________________ GB`
- [ ] Container disk size noted: `_____________________ GB`

### **Check Local Docker Build**

```bash
# Check if image exists locally
docker images | grep metroa-backend

# Expected output:
# macoaurelio/metroa-backend   latest   <image-id>   <time>   <size>
```

### **Verify Image is Pushed to Docker Hub**

```bash
# Check Docker Hub (or visit https://hub.docker.com/r/macoaurelio/metroa-backend)
docker pull macoaurelio/metroa-backend:latest

# If it works, the image is available on Docker Hub
```

### **If Image Not Pushed Yet**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Login to Docker Hub (if not already)
docker login

# Build and push (if not done already)
./deploy.sh
```

**⚠️ IMPORTANT:** Only proceed after Docker image is pushed to Docker Hub!

---

## **Step 2: Terminate Current Pod(s)**

### **🛑 Termination Checklist**

1. [ ] Open [RunPod Console](https://www.runpod.io/console/pods)
2. [ ] Locate pod(s) to terminate
3. [ ] Click "Terminate" on each pod
4. [ ] Confirm termination
5. [ ] Verify pod status shows "Terminated"

### **Option A: Terminate via RunPod Console (Recommended)**

1. Go to [RunPod Console - Pods](https://www.runpod.io/console/pods)
2. Find your current pod(s)
3. Click on the pod to open details
4. Click **"Terminate"** button (or **"Stop"** then **"Terminate"**)
5. Confirm termination
6. Wait for pod status to show **"Terminated"**

### **Option B: Multiple Pods**

If you have multiple pods to terminate:

1. Go to [RunPod Console - Pods](https://www.runpod.io/console/pods)
2. Check the boxes next to pods you want to terminate
3. Click **"Terminate Selected"** (or use bulk actions)
4. Confirm termination

### **⚠️ Before Terminating - Save Important Info**

**Save these details from your current pod:**

- Pod ID: `k0r2cn19yf6osw` (or similar)
- Proxy URL: `https://k0r2cn19yf6osw-8888.proxy.runpod.net`
- GPU Type: RTX 4090 (or other)
- Container Disk Size: 40 GB (or other)
- Volume Disk Size: 50 GB (or other)
- Volume Mount Path: `/workspace`

**How to save:**
- Take a screenshot of pod configuration
- Or copy the pod details from the RunPod console

---

## **Step 3: Deploy New Pod**

### **🚀 Deployment Checklist**

- [ ] **GPU:** RTX 4090 (or other)
- [ ] **Container Image:** `macoaurelio/metroa-backend:latest`
- [ ] **Container Disk:** `40-80 GB`
- [ ] **Volume:** `50-100 GB` at `/workspace`
- [ ] **Port:** `8888` (HTTP/Public)
- [ ] **SSH:** Enabled (optional)

### **3.1 Navigate to RunPod Console**

Go to: [https://www.runpod.io/console/pods](https://www.runpod.io/console/pods)

Click **"Deploy"** or **"Create Pod"** button.

### **3.2 Select GPU Template**

**Recommended:**
- **GPU:** RTX 4090 (24 GB VRAM)
- **Template:** Community or CUDA-enabled template

**Alternative Options:**
- RTX 3090 (24 GB) - Good performance
- RTX 4080 (16 GB) - Good for testing
- A6000 (48 GB) - For very large reconstructions

### **3.3 Configure Container Settings**

#### **Container Image**
```
macoaurelio/metroa-backend:latest
```

#### **Container Disk**
- **Size:** `40 GB` (minimum)
- **Recommended:** `50-80 GB` (for processing space)

#### **Docker Command** (Optional - defaults are fine)
Leave empty (uses CMD from Dockerfile)

#### **Container Disk Path**
Default is fine (usually `/workspace`)

### **3.4 Configure Volume (Persistent Storage)**

#### **Create New Volume or Use Existing**

**Option A: Use Existing Volume** (Recommended - preserves data)
- Select existing volume with 50+ GB
- **Mount Path:** `/workspace`
- This keeps your database and previous reconstructions

**Option B: Create New Volume**
- **Size:** `50 GB` minimum, `100 GB` recommended
- **Name:** `metroa-backend-data` (or similar)
- **Mount Path:** `/workspace`

**⚠️ IMPORTANT:** Volume at `/workspace` stores:
- SQLite database (`/workspace/database.db`)
- Uploaded videos (`/workspace/data/uploads/`)
- Reconstructed point clouds (`/workspace/data/results/`)
- Cache files (`/workspace/data/cache/`)

### **3.5 Network Configuration**

#### **Expose Port**
- **Port:** `8888`
- **Type:** `HTTP` or `Public`

This creates the proxy URL: `https://<POD-ID>-8888.proxy.runpod.net`

### **3.6 Environment Variables** (Optional)

Add if needed:
```
DATABASE_PATH=/workspace/database.db
CUDA_VISIBLE_DEVICES=0
```

### **3.7 Advanced Settings** (Optional)

- **Jupyter:** Disabled (we use FastAPI)
- **Connect via SSH:** Enabled (useful for debugging)
- **Preemptible:** Depends on your needs
- **Auto Shutdown:** Set to desired timeout (e.g., 1 hour)

### **3.8 Deploy Pod**

1. [ ] Click "Deploy" in RunPod Console
2. [ ] Select GPU template
3. [ ] Enter container image name
4. [ ] Set container disk size
5. [ ] Configure volume (use existing or create new)
6. [ ] Set port 8888 to expose
7. [ ] Review and deploy
8. [ ] Wait for pod to be "Running"

---

## **Step 4: Verify Pod Deployment**

### **✅ Post-Deployment Verification Checklist**

- [ ] **New Pod ID:** `_____________________`
- [ ] **New Proxy URL:** `https://_______________-8888.proxy.runpod.net`
- [ ] Pod status: "Running"
- [ ] Health check works: `curl https://<POD-ID>-8888.proxy.runpod.net/health`
- [ ] API status works: `curl https://<POD-ID>-8888.proxy.runpod.net/api/status`
- [ ] Pod logs show successful startup
- [ ] Database initialized (check logs)

### **4.1 Check Pod Status**

In RunPod Console, pod should show:
- Status: **"Running"** (green)
- All services: **Healthy**

### **4.2 Get New Pod URL**

After deployment, you'll see:
- **Pod ID:** `abc123xyz456` (example)
- **Proxy URL:** `https://abc123xyz456-8888.proxy.runpod.net`

**Copy this URL!** You'll need it for the frontend.

### **4.3 Test Backend Health**

Open in browser or run:
```bash
# Test health endpoint
curl https://<NEW-POD-ID>-8888.proxy.runpod.net/health

# Expected response:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/database.db"}
```

### **4.4 Test API Status**

```bash
curl https://<NEW-POD-ID>-8888.proxy.runpod.net/api/status

# Expected: JSON with backend status and project info
```

### **4.5 Check Logs** (Optional)

In RunPod Console:
1. Click on your pod
2. Go to **"Logs"** tab
3. Should see FastAPI startup messages:
   ```
   🚀 Starting up COLMAP Backend...
   ✅ Database initialized
   ✅ Demo data initialized successfully
   🎯 COLMAP Backend ready!
   INFO:     Uvicorn running on http://0.0.0.0:8888
   ```

---

## **Step 5: Update Frontend Connection**

### **🔗 Frontend Update Checklist**

- [ ] Updated Vercel env var: `NEXT_PUBLIC_API_URL`
  - Old: `https://_______________-8888.proxy.runpod.net`
  - New: `https://_______________-8888.proxy.runpod.net`
- [ ] Vercel redeployed: `vercel --prod --force`
- [ ] Frontend loads without errors
- [ ] Frontend can connect to backend
- [ ] Browser console shows no 404 errors

### **5.1 Update Vercel Environment Variable**

**Option A: Via Vercel Dashboard** (Recommended)

1. Go to: [https://vercel.com/interact-hq/metroa-demo/settings/environment-variables](https://vercel.com/interact-hq/metroa-demo/settings/environment-variables)
2. Find `NEXT_PUBLIC_API_URL`
3. Click **Edit**
4. Update value to: `https://<NEW-POD-ID>-8888.proxy.runpod.net`
5. Make sure it's enabled for **Production** ✓
6. Click **Save**

**Option B: Via Vercel CLI**

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Create/update .env.production
echo 'NEXT_PUBLIC_API_URL="https://<NEW-POD-ID>-8888.proxy.runpod.net"' > .env.production

# Redeploy with new env var
vercel --prod --force
```

### **5.2 Verify Frontend Connection**

1. Open frontend: https://metroa-demo.vercel.app
2. Check browser console (F12) - should see no 404 errors
3. Navigate to dashboard - should load projects
4. Try uploading a test video (if you have one)

---

## **Step 6: Final Verification**

### **🎯 Final Verification Checklist**

- [ ] Pod is running and healthy
- [ ] Backend health endpoint responds: `/health`
- [ ] API status endpoint works: `/api/status`
- [ ] Frontend environment variable updated
- [ ] Frontend deployed with new backend URL
- [ ] Frontend can connect to backend (no 404s)
- [ ] Database initialized (check logs)
- [ ] Demo data loaded (if needed)
- [ ] Test upload works
- [ ] Projects load in dashboard
- [ ] Backend responds to all API calls
- [ ] Database persists data (if using same volume)
- [ ] GPU processing works (test a reconstruction)

---

## **Troubleshooting**

### **Pod Won't Start**

**Symptoms:** Pod stuck in "Starting" or "Error" state

**Solutions:**
1. Check pod logs for error messages
2. Verify Docker image exists: `docker pull macoaurelio/metroa-backend:latest`
3. Check container disk size (needs 40+ GB)
4. Try deploying with different GPU template
5. Check RunPod status page for outages

### **Backend Not Responding**

**Symptoms:** 502/503 errors or connection timeout

**Solutions:**
1. Wait 1-2 minutes after pod start (initialization time)
2. Check pod logs for startup errors
3. Verify port 8888 is exposed correctly
4. Test direct proxy URL in browser
5. Check firewall/security settings

### **Database Not Initializing**

**Symptoms:** API returns errors about database

**Solutions:**
1. Check volume is mounted at `/workspace`
2. Check pod logs for database errors
3. Verify volume has enough space
4. Check permissions on `/workspace` directory

### **Frontend Can't Connect**

**Symptoms:** Frontend shows 404 or connection errors

**Solutions:**
1. Verify `NEXT_PUBLIC_API_URL` environment variable is set correctly
2. Check Vercel deployment completed successfully
3. Clear browser cache and hard refresh (Cmd+Shift+R)
4. Check browser console for specific error messages
5. Verify backend URL format: `https://<POD-ID>-8888.proxy.runpod.net`

### **Old Data Missing**

**Symptoms:** Previous reconstructions not showing

**Solutions:**
1. **If using new volume:** Data is in old volume, attach old volume instead
2. **If using same volume:** Data should be preserved, check volume mount path
3. Check database location: `/workspace/database.db`
4. Restore from backup if available

---

## **Quick Reference: Pod Configuration Template**

```
GPU: RTX 4090 (24 GB)
Container Image: macoaurelio/metroa-backend:latest
Container Disk: 40-80 GB
Volume: 50-100 GB (mounted at /workspace)
Port: 8888 (HTTP/Public)
Environment Variables:
  - DATABASE_PATH=/workspace/database.db
SSH: Enabled (optional, for debugging)
Auto Shutdown: 1 hour (optional)
```

---

## **Best Practices**

1. **Always verify Docker image is pushed before terminating pods**
2. **Save pod configuration before terminating** (screenshot or notes)
3. **Use persistent volumes** for database and user data
4. **Test backend health** before updating frontend
5. **Monitor pod logs** during first few minutes
6. **Keep old pod running** until new one is verified (if possible)
7. **Update frontend after backend is confirmed working**

---

## **Quick Command Reference**

```bash
# Check Docker image locally
docker images | grep metroa-backend

# Pull latest from Docker Hub (verify it's available)
docker pull macoaurelio/metroa-backend:latest

# Test backend health (replace with your pod ID)
curl https://<POD-ID>-8888.proxy.runpod.net/health

# Test API status
curl https://<POD-ID>-8888.proxy.runpod.net/api/status

# Update and redeploy frontend
cd /Users/marco.aurelio/Desktop/metroa-demo
echo 'NEXT_PUBLIC_API_URL="https://<POD-ID>-8888.proxy.runpod.net"' > .env.production
vercel --prod --force
```

---

## **Quick Links**

- RunPod Console: https://www.runpod.io/console/pods
- Vercel Dashboard: https://vercel.com/interact-hq/metroa-demo
- Vercel Env Vars: https://vercel.com/interact-hq/metroa-demo/settings/environment-variables

---

## **Cost Optimization Tips**

1. **Use preemptible instances** for testing (lower cost)
2. **Set auto-shutdown** to avoid idle charges
3. **Terminate pods when not in use**
4. **Use smaller container disk** if possible (40 GB minimum)
5. **Monitor usage** in RunPod dashboard

---

## **Next Steps After Deployment**

1. Test video upload and reconstruction
2. Verify all endpoints are working
3. Check processing quality matches expectations
4. Monitor resource usage (GPU, memory, disk)
5. Set up monitoring/alerts if needed

---

## **Notes Section**

**Date:** `_____________________`

**Issues Encountered:**
```
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

**Resolution:**
```
_____________________________________________________
_____________________________________________________
_____________________________________________________
```

---

**Need Help?**

- RunPod Docs: https://docs.runpod.io/
- RunPod Support: https://www.runpod.io/support
- Check pod logs for detailed error messages

---

**✅ All checklist items completed? You're ready to go!**
