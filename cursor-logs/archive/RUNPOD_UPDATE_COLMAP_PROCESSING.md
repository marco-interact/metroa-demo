# RunPod Update: COLMAP Video Processing

## ✅ What's New

Video uploads now trigger **actual COLMAP 3D reconstruction**:

1. **Frame Extraction** (20% progress)
2. **SIFT Feature Detection** (40% progress)
3. **Feature Matching** (60% progress)
4. **Sparse Reconstruction** (80% progress)
5. **PLY Export** (90% progress)
6. **Complete** (100% progress)

The frontend will show live progress updates as the reconstruction runs in the background!

---

## 🚀 Update Commands for RunPod

**Copy and paste this entire block into RunPod web terminal:**

```bash
# Navigate to workspace
cd /workspace/colmap-mvp

# Pull latest code
git fetch origin && git reset --hard origin/main

# Activate virtual environment
source venv/bin/activate

# Stop old backend
pkill -f "python.*main.py"

# Start backend with new COLMAP processing
nohup python main.py > backend.log 2>&1 &

# Wait for startup
sleep 10

# Verify backend is running
curl http://localhost:8000/health

# Check latest commits
git log --oneline -3
```

---

## ✅ Verification

After running the update, check the backend log:

```bash
tail -f /workspace/colmap-mvp/backend.log
```

You should see:
- `🎯 COLMAP Backend ready!`
- `INFO: Application startup complete.`

---

## 🎬 Test Video Processing

1. Go to frontend: https://colmap-q2i6zbivn-interact-hq.vercel.app
2. Create a new scan
3. Upload a video
4. Watch the progress bar update in real-time:
   - 0% → Queued
   - 20% → Extracting frames
   - 40% → Detecting features
   - 60% → Matching features
   - 80% → Building 3D model
   - 90% → Exporting
   - 100% → Complete!

---

## 📊 What Happens Behind the Scenes

When you upload a video:

1. **Video saved** to `/workspace/data/uploads/{scan_id}/`
2. **Scan record created** in database with status `processing`
3. **Background task queued** to run COLMAP pipeline
4. **Status updates** as each stage completes:
   - `extracting_frames` → `extracting_features` → `matching_features` → `reconstructing` → `exporting` → `completed`
5. **PLY file saved** to `/workspace/data/results/{scan_id}/sparse/0/points3D.ply`
6. **Database updated** with PLY file path

Frontend polls `/api/jobs/{job_id}` every 2 seconds to get progress updates.

---

## 🔍 Monitoring Live Reconstruction

Watch the backend process a video in real-time:

```bash
tail -f /workspace/colmap-mvp/backend.log
```

You'll see emoji-marked stages:
- 📹 Extracting frames
- 🔍 Extracting SIFT features
- 🔗 Matching features
- 🏗️ Running sparse reconstruction
- 💾 Exporting to PLY
- ✅ COLMAP reconstruction complete

---

## ⚠️ Important Notes

- **Processing time**: Depends on video length and quality setting
  - Low: ~2-5 minutes
  - Medium: ~5-10 minutes
  - High: ~10-20+ minutes

- **GPU acceleration**: COLMAP uses GPU for feature extraction if available

- **Persistence**: All data saved to `/workspace` (persistent volume)

- **Error handling**: If reconstruction fails, scan status will be `failed: {error message}`

---

## 🎯 Next Steps

After updating RunPod, the video processing will work end-to-end!

No Vercel changes needed - the frontend already polls for job status and will automatically show the progress updates.

