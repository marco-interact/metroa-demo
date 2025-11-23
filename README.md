# Metroa Labs - 3D Reconstruction Platform

Professional videogrammetry platform powered by COLMAP and Next.js. Upload videos, get high-quality 3D point clouds with measurement tools.

---

## 🚀 **Quick Start (BYOC Deployment)**

We use a **Bring Your Own Container (BYOC)** workflow for RunPod to ensure maximum performance and stability.

### **1. Build & Push (Latest Only)**

The deployment script now defaults to `latest`, cleaning up old local builds automatically.

```bash
# Make executable
chmod +x deploy.sh

# Build and push 'latest'
./deploy.sh
```

### **2. Deploy on RunPod**

1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. **Deploy** a new pod (RTX 4090 recommended)
3. **Container Image:** `macoaurelio/metroa-backend:latest`
4. **Container Disk:** 40 GB+
5. **Volume Disk:** 50 GB+ (Mount path: `/workspace`)
6. **Expose Port:** `8888`
7. **Start Pod**

> **Note on Updates:** Since we are using `:latest`, you must **Stop** and then **Start** your pod to pull new changes. A simple restart might use the cached image.


### **3. Connect Frontend**

Update your Vercel environment variable:
```env
NEXT_PUBLIC_API_URL="https://YOUR-POD-ID-8888.proxy.runpod.net"
```

---

## 📁 **Project Structure**

```
metroa-demo/
├── deploy.sh                     # 🚀 Unified deployment script (Build & Push)
├── Dockerfile                    # Optimized production Dockerfile
├── start-backend.sh              # Robust container entrypoint
├── requirements.txt              # Python dependencies
├── main.py                       # FastAPI Backend
├── colmap_processor.py           # 3D Reconstruction Pipeline
├── mesh_generator.py             # Mesh Generation
├── src/                          # Next.js Frontend
└── README/                       # Documentation & Scripts
    ├── archive/                  # Old documentation
    └── scripts/                  # Helper scripts
```

---

## 🏗️ **Architecture**

```
Frontend (Next.js)          Backend (FastAPI)           GPU Processing
─────────────────          ─────────────────           ──────────────
┌───────────────┐          ┌───────────────┐          ┌─────────────┐
│   React UI    │  HTTP    │  FastAPI      │  Calls   │   COLMAP    │
│   Three.js    ├────────→ │  Endpoints    ├────────→ │   (CUDA)    │
│   Tailwind    │          │  SQLite DB    │          │   OpenMVS   │
└───────────────┘          └───────────────┘          │   Open3D    │
                                                       └─────────────┘
Deployed on:               Deployed on:                Runs in:
Vercel                     RunPod (Docker)             Docker Container
```

---

## 🔧 **Local Development**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Backend
python main.py

# Run Frontend
npm run dev
```

---

## 📝 **License**

Proprietary - Metroa Labs
