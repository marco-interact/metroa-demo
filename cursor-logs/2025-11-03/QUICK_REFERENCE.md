# Quick Reference Guide - RunPod COLMAP Deployment

## 🚀 One-Command Setup

Copy and paste this into your RunPod web terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/marco-interact/colmap-demo/main/runpod-setup.sh | bash
```

Or if already cloned:

```bash
cd /workspace && git clone https://github.com/marco-interact/colmap-demo.git
cd colmap-demo && chmod +x runpod-setup.sh && ./runpod-setup.sh
```

---

## 📝 Pod Information

| Item | Value |
|------|-------|
| **Pod ID** | `xhqt6a1roo8mrc` |
| **Pod Name** | colmap_worker_gpu |
| **Storage Volume ID** | `rrtms4xkiz` |
| **Storage Name** | colmap-gpu-volume |
| **GitHub Repo** | https://github.com/marco-interact/colmap-demo.git |
| **Vercel Team** | interact-hq |
| **Vercel Team ID** | `team_PWckdPO4Vl3C1PWOA9qs9DrI` |

---

## ⚡ Quick Commands

### Start Backend Server

```bash
/workspace/start-colmap.sh
```

or manually:

```bash
cd /workspace/colmap-demo
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Stop Backend Server

```bash
lsof -ti:8000 | xargs kill -9
```

### Restart Backend

```bash
lsof -ti:8000 | xargs kill -9 && /workspace/start-colmap.sh
```

### Update Code from GitHub

```bash
cd /workspace/colmap-demo && git pull origin main
```

### Rebuild Python Dependencies

```bash
cd /workspace/colmap-demo
source venv/bin/activate
pip install -r requirements.txt
```

### Check Backend Status

```bash
curl http://localhost:8000/health
```

### View Demo Projects

```bash
curl http://localhost:8000/api/projects
```

---

## 🌐 Endpoints

### Backend API

**Local**: http://localhost:8000  
**Public**: http://xhqt6a1roo8mrc-8000.proxy.runpod.net

### API Routes

- `GET /health` - Health check
- `GET /api/projects` - List all projects
- `GET /api/projects/{project_id}` - Get project details
- `POST /api/upload` - Upload images for processing
- `POST /api/process` - Start COLMAP processing
- `GET /api/results/{result_id}` - Get processing results

---

## 🎨 Vercel Frontend Deployment

### Install Vercel CLI

```bash
npm install -g vercel
```

### Deploy to Vercel

```bash
cd /workspace/colmap-demo

# Install dependencies
npm install

# Build the application
npm run build

# Deploy to production
vercel --prod --scope interact-hq --yes
```

### Set Environment Variable in Vercel

After deployment, add this environment variable in Vercel dashboard:

```
NEXT_PUBLIC_API_URL=http://xhqt6a1roo8mrc-8000.proxy.runpod.net
```

Or via CLI:

```bash
vercel env add NEXT_PUBLIC_API_URL production
# Then paste: http://xhqt6a1roo8mrc-8000.proxy.runpod.net
```

---

## 🔍 Monitoring & Debugging

### GPU Status

```bash
nvidia-smi
```

### Real-time GPU Monitoring

```bash
watch -n 1 nvidia-smi
```

### Check Disk Space

```bash
df -h /workspace
```

### View Backend Logs (Debug Mode)

```bash
cd /workspace/colmap-demo
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
```

### Check Data Directory Size

```bash
du -sh /workspace/colmap-demo/data/*
```

### Test COLMAP

```bash
colmap -h
```

---

## 🛠️ Troubleshooting

### COLMAP Not Found

```bash
export PATH="/workspace/colmap/bin:$PATH"
echo 'export PATH="/workspace/colmap/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Database Issues

```bash
cd /workspace/colmap-demo
source venv/bin/activate
rm -f data/database.db
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
```

### Port Already in Use

```bash
lsof -ti:8000 | xargs kill -9
```

### Permission Issues

```bash
cd /workspace/colmap-demo
chmod +x runpod-setup.sh
chmod +x /workspace/start-colmap.sh
```

### Clean Rebuild

```bash
cd /workspace/colmap-demo
rm -rf venv data/database.db __pycache__
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
```

---

## 📦 File Structure

```
/workspace/colmap-demo/
├── main.py                 # FastAPI backend
├── database.py             # Database management
├── colmap_processor.py     # COLMAP processing logic
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── runpod-setup.sh        # Automated setup script
├── data/
│   ├── results/           # Processing results
│   ├── cache/             # Temporary cache
│   └── uploads/           # Uploaded images
├── src/                   # Next.js frontend
├── demo-resources/        # Demo scans and models
└── cursor-logs/           # Development logs and documentation
```

---

## 🔐 Environment Variables

These are automatically set by the setup script:

```bash
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1
```

---

## 📊 Testing

### Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test Projects Endpoint

```bash
curl http://localhost:8000/api/projects | jq
```

### Test Specific Demo Scan

```bash
curl http://localhost:8000/api/projects/demoscan-dollhouse | jq
```

---

## 🔄 Update Workflow

1. Make changes locally in Cursor
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```

3. Pull changes on RunPod:
   ```bash
   cd /workspace/colmap-demo
   git pull origin main
   ```

4. Restart backend:
   ```bash
   lsof -ti:8000 | xargs kill -9
   /workspace/start-colmap.sh
   ```

5. Redeploy frontend (if needed):
   ```bash
   cd /workspace/colmap-demo
   npm run build
   vercel --prod --scope interact-hq --yes
   ```

---

## 📞 Support

For detailed setup instructions, see:
- **Full Deployment Guide**: `/workspace/colmap-demo/cursor-logs/2025-11-03/RUNPOD_DEPLOYMENT_GUIDE.md`
- **GitHub Repository**: https://github.com/marco-interact/colmap-demo

---

*Last Updated: 2025-11-03*

