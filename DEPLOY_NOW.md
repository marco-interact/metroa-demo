# 🚀 Deploy & Test Full Pipeline

## ✅ What's Ready to Test

- ✅ **Mesh Generation**: Automatic GLB mesh creation
- ✅ **Dense Reconstruction**: 1M-8M points per room
- ✅ **Quality Presets**: Fast, High Quality, Ultra modes
- ✅ **Clean UI**: Single loader, percentage-based progress
- ✅ **Web App Testing**: Upload through interface, no CLI needed!

---

## 📦 Deploy Backend to RunPod

### Step 1: SSH into RunPod

```bash
ssh root@203.57.40.132 -p 10164
```

### Step 2: Update & Restart Backend

```bash
# Navigate to project
cd /workspace/metroa-demo

# Pull latest code (mesh generation + all fixes)
git pull metroa main

# Stop existing backend
kill $(cat backend.pid 2>/dev/null) 2>/dev/null || pkill -f "uvicorn main:app"

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies (mesh_generator.py needs Open3D)
pip install open3d==0.19.0

# Start backend with GPU support
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Verify backend is running
sleep 3
curl http://localhost:8888/health

# Check logs
tail -20 backend.log
```

**Expected output:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "colmap_version": "3.10",
  "mesh_generation": "enabled"
}
```

### Step 3: Monitor Logs (Optional)

```bash
# Watch logs in real-time
tail -f /workspace/metroa-demo/backend.log

# Filter for mesh generation
tail -f /workspace/metroa-demo/backend.log | grep -E "mesh|Mesh|🔨|✅"
```

---

## 🌐 Deploy Frontend to Vercel

### From Your Mac Terminal

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Deploy to Vercel
npx vercel --prod

# Or if you have vercel CLI installed
vercel --prod
```

**Follow the prompts:**
1. Confirm project linking (should link to existing Vercel project)
2. Wait for build (~2-3 minutes)
3. Get deployment URL

**Expected output:**
```
✔ Deployed to production. Run `vercel --prod` to overwrite later.
🔍 Inspect: https://vercel.com/...
✅ Production: https://your-app.vercel.app
```

---

## 🧪 Test Through Web App

### 1. Open App in Browser

```
https://your-app.vercel.app
```

### 2. Login (if needed)

Use your credentials or the demo account.

### 3. Create/Select Project

- Click "New Project" or select existing
- Name it "Mesh Test" or similar

### 4. Upload Video

- Click "Upload Scan" or "New Scan"
- Select your 40-second video
- Choose quality: **High Quality** (recommended for testing)
- Click "Start Reconstruction"

### 5. Monitor Progress

You should see:
- ✅ Single loading animation (no double loaders!)
- ✅ Stage-by-stage progress with percentages:
  ```
  ✓ Frame Extraction (100%)
  ⟳ Feature Extraction (45%)
  ○ Feature Matching (—)
  ○ Sparse Reconstruction (—)
  ○ Dense Reconstruction (—)
  ○ Post-Processing (—)
  ○ Mesh Generation (—)  ← NEW STAGE!
  ```

### 6. Expected Timeline

| Quality | Frames | Time | Points | Triangles |
|---------|--------|------|--------|-----------|
| **Fast** | 200-280 | 2-3 min | 1M-3M | ~300K |
| **High Quality** | 280-400 | 3-5 min | 3M-8M | ~500K |
| **Ultra** | 400+ | 5-8 min | 5M-10M | ~1M |

### 7. View Results

Once complete:
- ✅ 3D viewer loads automatically
- ✅ Dense point cloud visible
- ✅ Download buttons for PLY and GLB (mesh)
- ✅ Smooth, professional visualization

---

## 📊 Verify Mesh Generation

### Check Backend Logs (on RunPod)

```bash
# SSH into RunPod
ssh root@203.57.40.132 -p 10164

# Check recent mesh generation
tail -50 /workspace/metroa-demo/backend.log | grep -E "mesh|Mesh|🔨"
```

**Look for:**
```
🔨 Generating mesh from point cloud: /workspace/data/results/.../pointcloud_final.ply
✅ Mesh generated: 261,573 vertices, 523,145 triangles
```

### Check Files Created

```bash
# List recent reconstructions
ls -lht /workspace/data/results/ | head -10

# Check specific scan directory
ls -lh /workspace/data/results/SCAN_ID_HERE/

# Should see:
# - pointcloud_final.ply (dense point cloud)
# - mesh.glb (3D mesh)  ← NEW!
# - frames/ (extracted frames)
```

### Check Database

```bash
# On RunPod
sqlite3 /workspace/database.db

# Query mesh data
SELECT id, name, point_count_final, mesh_triangles, mesh_vertices 
FROM scans 
WHERE mesh_file IS NOT NULL 
ORDER BY created_at DESC 
LIMIT 5;

# Exit
.quit
```

---

## 🎯 What to Look For

### ✅ Success Indicators

1. **Dense Point Cloud**: 2-8M points (not 200K!)
2. **Mesh Generated**: 300K-1M triangles
3. **Smooth Visualization**: No giant cubes, smooth surfaces
4. **Complete Room**: Full coverage of video footage
5. **Download Works**: Both PLY and GLB files available

### ❌ Issues to Report

1. **Still Sparse**: <1M points after 40-second video
2. **No Mesh**: mesh.glb file missing
3. **Blocky**: Large cube artifacts in point cloud
4. **Incomplete**: Missing parts of room
5. **Errors**: Processing fails or hangs

---

## 🐛 Troubleshooting

### Backend Not Responding

```bash
# SSH into RunPod
ssh root@203.57.40.132 -p 10164

# Check if backend is running
curl http://localhost:8888/health

# If not running, restart
cd /workspace/metroa-demo
kill $(cat backend.pid 2>/dev/null) || pkill -f "uvicorn"
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

### Check Backend Logs for Errors

```bash
# SSH into RunPod
ssh root@203.57.40.132 -p 10164

# Check last 100 lines
tail -100 /workspace/metroa-demo/backend.log

# Check for errors
grep -i error /workspace/metroa-demo/backend.log | tail -20
```

### Frontend Not Connecting to Backend

Check `next.config.js` has correct backend URL:

```javascript
async rewrites() {
  return [
    {
      source: '/api/backend/:path*',
      destination: 'http://203.57.40.132:8888/api/:path*'
    }
  ]
}
```

### Mesh Generation Failed

**Check Open3D installed:**
```bash
# On RunPod
source /workspace/metroa-demo/venv/bin/activate
python3 -c "import open3d; print(open3d.__version__)"
# Should print: 0.19.0
```

**Check point cloud exists:**
```bash
# Find recent reconstruction
ls -lh /workspace/data/results/*/pointcloud_final.ply | tail -5

# If missing, check raw point cloud
ls -lh /workspace/data/results/*/fused.ply | tail -5
```

---

## 📝 Deployment Summary

### 1. Backend (RunPod) ✅
```bash
ssh root@203.57.40.132 -p 10164
cd /workspace/metroa-demo
git pull metroa main
kill $(cat backend.pid) || pkill -f uvicorn
source venv/bin/activate
pip install open3d==0.19.0
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
curl http://localhost:8888/health
```

### 2. Frontend (Vercel) ✅
```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
npx vercel --prod
```

### 3. Test in Browser ✅
- Open Vercel URL
- Upload 40-second video
- Select "High Quality" mode
- Wait 3-5 minutes
- Verify: Dense point cloud + mesh generated

---

## 🎬 Quick Test Script

Save this as `test_reconstruction.sh` on your Mac:

```bash
#!/bin/bash

echo "🚀 Testing Full Reconstruction Pipeline"
echo ""

# 1. Check backend health
echo "1️⃣ Checking backend..."
curl -s http://203.57.40.132:8888/health | python3 -m json.tool

# 2. Upload test video
echo ""
echo "2️⃣ Upload your video through the web app:"
echo "   👉 https://your-app.vercel.app"
echo ""
echo "3️⃣ Monitor progress in RunPod logs:"
echo "   ssh root@203.57.40.132 -p 10164"
echo "   tail -f /workspace/metroa-demo/backend.log"
echo ""
echo "✅ Look for: '✅ Mesh generated: X vertices, Y triangles'"
```

---

## 🎯 Expected Results

### Before This Update
- ❌ ~200K sparse points
- ❌ Giant cube artifacts
- ❌ No mesh generation
- ❌ Quality modes not working
- ❌ Incomplete room coverage

### After This Update
- ✅ 2-8M dense points
- ✅ Fine-grained detail
- ✅ Automatic mesh (300K-1M triangles)
- ✅ Quality modes fully functional
- ✅ Complete room reconstruction
- ✅ Web-compatible GLB format

---

## 📞 Support

If you encounter issues:

1. **Check backend logs**: `tail -100 backend.log`
2. **Verify GPU available**: `curl localhost:8888/health`
3. **Check disk space**: `df -h /workspace`
4. **Monitor memory**: `free -h`
5. **Check COLMAP**: `which colmap && colmap -h`

---

**Status**: ✅ Code pushed to GitHub  
**Next**: Deploy backend + frontend, test through web app!

