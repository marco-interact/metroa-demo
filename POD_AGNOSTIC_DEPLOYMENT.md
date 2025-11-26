# 🎯 Pod-Agnostic Deployment Guide

## ✅ Verification: Fully Pod-Agnostic

This Docker image is **100% pod-agnostic** and can be deployed to **any RunPod GPU instance** without modification.

### What Makes It Pod-Agnostic:

1. **No Hardcoded URLs**
   - ✅ No RunPod proxy URLs in code
   - ✅ No pod-specific IPs or hostnames
   - ✅ All URLs configured via environment variables (frontend only)

2. **Standard Paths**
   - ✅ Uses `/workspace` (RunPod standard mount point)
   - ✅ Database: `/workspace/database.db` (configurable via `DATABASE_PATH`)
   - ✅ Data: `/workspace/data/{results,uploads,cache}`

3. **Environment Variables**
   - ✅ `DATABASE_PATH` (optional, defaults to `/workspace/database.db`)
   - ✅ All other configs use sensible defaults

4. **Port Configuration**
   - ✅ Exposes port `8888` (standard FastAPI port)
   - ✅ No hardcoded ports in code

5. **GPU Compatibility**
   - ✅ Works on any NVIDIA GPU (RTX 3090, 4090, A6000, etc.)
   - ✅ CUDA architecture: 8.9 (Ada Lovelace) but compatible with older GPUs

---

## 🚀 Deployment Process

### Step 1: Build & Push (One-Time or When Code Changes)

```bash
./deploy.sh
```

This builds and pushes `macoaurelio/metroa-backend:latest` to Docker Hub.

### Step 2: Deploy to Any RunPod Pod

**Pod Settings:**
- **Container Image:** `macoaurelio/metroa-backend:latest`
- **Container Disk:** 60 GB (minimum)
- **Volume Disk:** 100 GB+ (recommended, mount at `/workspace`)
- **Exposed Port:** `8888` (TCP)
- **Environment Variables (Optional):**
  - `DATABASE_PATH=/workspace/database.db` (default, can be omitted)

**That's it!** The same image works on:
- ✅ RTX 3090 pods
- ✅ RTX 4090 pods  
- ✅ A6000 pods
- ✅ Any other NVIDIA GPU pod

### Step 3: Connect Frontend

**Only the frontend needs to know the pod URL:**

1. Get your pod's proxy URL: `https://[POD-ID]-8888.proxy.runpod.net`
2. Update Vercel environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://[POD-ID]-8888.proxy.runpod.net
   ```
3. Redeploy frontend

**Note:** When you switch pods, you only need to update the Vercel environment variable. The Docker image stays the same.

---

## 🔄 Pod Rotation Workflow

When moving to a new pod:

1. **Stop old pod** (optional, saves costs)
2. **Create new pod** with same settings:
   - Same image: `macoaurelio/metroa-backend:latest`
   - Same volume mount: `/workspace` (if using persistent volume)
3. **Update Vercel:**
   - Change `NEXT_PUBLIC_API_URL` to new pod's proxy URL
   - Redeploy frontend
4. **Done!** No Docker rebuild needed.

---

## 📋 Checklist: Pod-Agnostic Verification

Before deploying, verify:

- [x] No hardcoded RunPod URLs in `main.py`
- [x] No hardcoded pod IDs in any Python files
- [x] Database path uses environment variable
- [x] All paths use `/workspace` (standard mount)
- [x] Port 8888 is exposed (standard)
- [x] Dockerfile builds for `linux/amd64`
- [x] No pod-specific environment variables required

**Current Status:** ✅ All checks pass

---

## 🛠️ Troubleshooting

### Pod-Specific Issues

**Issue:** Backend not accessible
- **Check:** Pod proxy URL is correct in Vercel
- **Fix:** Update `NEXT_PUBLIC_API_URL` and redeploy frontend

**Issue:** Data not persisting
- **Check:** Volume is mounted at `/workspace`
- **Fix:** Ensure Network Volume is attached in pod settings

**Issue:** Permission errors
- **Check:** Startup script handles permissions automatically
- **Fix:** Restart pod (script runs `chmod 777 /workspace` on startup)

---

## 📝 Key Files (All Pod-Agnostic)

- **`Dockerfile`**: No pod-specific configs ✅
- **`start-backend.sh`**: Uses standard paths ✅
- **`main.py`**: Environment variables only ✅
- **`deploy.sh`**: Builds for `linux/amd64` ✅

---

## 🎯 Summary

**One Docker Image → Any RunPod Pod**

The image `macoaurelio/metroa-backend:latest` is:
- ✅ Fully pod-agnostic
- ✅ Works on any GPU pod
- ✅ No code changes needed when switching pods
- ✅ Only frontend URL needs updating

**Deployment is truly plug-and-play!** 🚀
