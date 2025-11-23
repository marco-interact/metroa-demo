# 🚀 Metroa Backend - Plug-and-Play Deployment Guide

This guide covers the **full scope** deployment of the Metroa 3D Reconstruction Backend on RunPod.

**Key Features:**
*   **Plug-and-Play:** One Docker image works on any RunPod GPU instance (RTX 3090/4090/A6000).
*   **Super High Definition:** Defaults to "Ultra" quality (COLMAP + OpenMVS + Open3D).
*   **Persistence Ready:** Automatically configures data storage in `/workspace` (works with or without attached volumes).
*   **Auto-Healing:** Robust startup script handles crashes and permission issues automatically.

---

## 🏗️ 1. Build & Push (One-Click)

Use the unified deployment script to build the optimized Docker image and push it to Docker Hub.
*This ensures you are always deploying the latest code.*

```bash
./deploy.sh
```

*Note: This builds the "Full Scope" image including COLMAP (CUDA), OpenMVS, and Open3D. It may take 30-45 minutes for the first build, but subsequent builds are faster due to caching.*

---

## ☁️ 2. RunPod Deployment (Plug-and-Play)

You can deploy this image to **any** GPU pod on RunPod.

### Recommended Specs
*   **GPU:** 1x RTX 4090 (Best performance/cost) or A6000 (Larger VRAM for huge datasets)
*   **Container Disk:** **60 GB** (Minimum) - *Crucial for the large Docker image*
*   **Volume Disk:** **100 GB+** (Recommended for persistent scan data)

### Deployment Steps
1.  **Select Pod:** Choose your GPU (e.g., RTX 4090).
2.  **Edit Template:**
    *   **Image Name:** `macoaurelio/metroa-backend:latest`
    *   **Container Disk:** `60` GB
    *   **Volume Disk:** `100` GB (Mount path: `/workspace`)
    *   **Exposed Ports:** `8888` (TCP)
3.  **Environment Variables (Optional):**
    *   `DATABASE_PATH`: `/workspace/database.db` (Default)
4.  **Start Pod.**

*The backend will automatically start, initialize the database, and begin serving on port 8888.*

---

## 🔄 3. Frontend Connection

Once the pod is running:

1.  **Get Pod ID:** (e.g., `v6934875-8888.proxy.runpod.net`)
2.  **Update Vercel/Frontend:**
    Set the `NEXT_PUBLIC_API_URL` environment variable in your Vercel project settings:
    ```
    NEXT_PUBLIC_API_URL=https://YOUR_POD_ID-8888.proxy.runpod.net
    ```
3.  **Redeploy Frontend.**

---

## 🛠️ Troubleshooting & Maintenance

### View Logs
To check backend status or debug crashes, open the Pod Web Terminal and run:
```bash
tail -f /tmp/backend-startup.log
```

### Manual Restart
If you need to restart the backend without restarting the whole pod:
```bash
pkill python3
nohup ./start-backend.sh &
```

### Persistence
*   **With Volume:** Data in `/workspace/data` persists across pod restarts/terminations.
*   **Without Volume:** Data in `/workspace/data` is lost when the pod is terminated (but persists during restarts).

---

## 📁 Project Structure (Optimized)

*   **`Dockerfile`**: The single source of truth for the production environment.
*   **`start-backend.sh`**: The brain of the operation. Handles environment setup, permissions, Xvfb, and process management.
*   **`main.py`**: The FastAPI application entry point.
*   **`colmap_processor.py`**: The "Ultra" quality pipeline logic.

