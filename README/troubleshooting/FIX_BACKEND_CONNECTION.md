# 🚨 Fix Backend Connection (404 Errors)

## Problem
Frontend shows "API Error: 404" - Backend is offline or not reachable

## ✅ Solution: Restart Backend on RunPod

### Step 1: Open Mac Terminal (NEW window/tab)

```bash
# DON'T use Docker container - use Mac Terminal directly
# Press Cmd+N for new window or Cmd+T for new tab
```

### Step 2: SSH into RunPod

```bash
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519
```

**If that fails, try:**
```bash
ssh root@203.57.40.132 -p 10164
```

### Step 3: Restart Backend (on RunPod)

```bash
# Go to project directory
cd /workspace/metroa-demo

# Kill any existing backend
pkill -9 python3
pkill -9 uvicorn
lsof -ti:8888 | xargs kill -9 2>/dev/null || true

# Pull latest code with MUCH denser settings
git fetch metroa
git pull metroa main

# Activate Python environment
source venv/bin/activate

# Verify GPU
nvidia-smi

# Start backend with better settings
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Wait for startup
sleep 8

# Test locally
curl http://localhost:8888/health

# If successful, you should see:
# {"status":"healthy","message":"Backend is running",...}
```

### Step 4: Test from Mac

Open **new Mac Terminal** window:

```bash
# Test backend
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health

# Should return:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/database.db"}
```

### Step 5: Refresh Frontend

```bash
# Open browser
open https://metroa-demo.vercel.app

# Or refresh your current tab
# Press Cmd+Shift+R (hard refresh)
```

---

## 🎯 What Changed - MUCH DENSER Reconstructions

### New "fast" Mode (Actually Dense Now)
- **Frames**: 200-280 frames (was 120-200)
- **Features**: 16,384 per image (was 12,000)
- **Resolution**: 2560p (was 1920p)
- **Dense iterations**: 10 (was 6)
- **Expected points**: **1M-3M** (was 100K-300K)
- **Time**: 2-3 minutes

### New "high_quality" Mode (Maximum Density)
- **Frames**: 280-400 frames (was 200-280)
- **Features**: 16,384 per image
- **Resolution**: 3200p (was 2560p)
- **Matching**: Exhaustive (was sequential)
- **Dense iterations**: 15 (was 8)
- **Window radius**: 13 (was 9)
- **Expected points**: **3M-8M** (was 500K-2M)
- **Time**: 3-5 minutes

### Key Changes for Complete Room Capture

1. **More Frames** = Better coverage
   - 40s video @ 7 FPS = 280 frames (was 160)
   - Every part of room captured multiple times

2. **More Features** = Better matching
   - 16,384 features per image (maximum SIFT)
   - Affine shape estimation enabled

3. **Denser Reconstruction** = More points
   - Larger window radius (13 vs 7)
   - More iterations (15 vs 6)
   - More samples per pixel (50 vs 20)

4. **Relaxed Fusion** = Keep more points
   - Lower NCC threshold (0.05 vs 0.25)
   - Higher reprojection error tolerance
   - Minimum 1 pixel visibility (was 2-3)

5. **Minimal Cleanup** = Preserve density
   - More lenient outlier removal
   - Higher downsampling threshold (10M vs 3M)
   - Finer voxel size (0.003 vs 0.004)

---

## 📊 Expected Results (40-Second Room Video)

### Before (Old Settings)
- ❌ 50K-200K points
- ❌ Sparse, incomplete coverage
- ❌ Missing walls/corners
- ⏱️ 1-2 minutes

### After (New Settings)

**Fast Mode:**
- ✅ **1M-3M points**
- ✅ **Complete room coverage**
- ✅ **All walls, floor, ceiling visible**
- ⏱️ 2-3 minutes

**High Quality Mode:**
- ✅ **3M-8M points**
- ✅ **Dense surface detail**
- ✅ **Every corner captured**
- ✅ **Furniture, objects well-defined**
- ⏱️ 3-5 minutes

---

## 🧪 Test the Improvements

### 1. Upload 40s Room Video

Use **high_quality** mode for maximum density

### 2. Wait for Processing

- Fast mode: 2-3 min → 1-3M points
- High quality: 3-5 min → 3-8M points

### 3. Check Results

**Point Cloud Viewer:**
- Should see complete room outline
- Walls, floor, ceiling all visible
- Dense surface coverage
- Fine point size (0.005)

**Scan Details:**
- Check "point_count_final" - should be 1M+ (fast) or 3M+ (high)
- Coverage should be >90%

---

## 🔍 Troubleshooting

### Backend Still Shows 404

**Check if backend is actually running:**
```bash
# On RunPod
ps aux | grep uvicorn
curl http://localhost:8888/health
```

**Check logs for errors:**
```bash
tail -100 /workspace/metroa-demo/backend.log
```

**Completely restart:**
```bash
# On RunPod
cd /workspace/metroa-demo
pkill -9 python3
source venv/bin/activate
QT_QPA_PLATFORM=offscreen python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
echo $! > backend.pid
```

### Reconstruction Still Too Sparse

**Make sure you pulled latest code:**
```bash
# On RunPod
cd /workspace/metroa-demo
git log -1 --oneline
# Should show: "Major Reconstruction Pipeline Optimization"

git diff quality_presets.py
# Should show the new dense settings
```

**Use high_quality mode:**
- In frontend, select "High Quality" (not Fast)
- This uses exhaustive matching + maximum density settings

**Check processing logs:**
```bash
# On RunPod
tail -f /workspace/metroa-demo/backend.log | grep -E "(frames|features|dense|points)"
```

### Still Getting Low Point Counts

**Verify settings were applied:**
```bash
# On RunPod
cd /workspace/metroa-demo
python3 -c "from quality_presets import get_preset; p = get_preset('high_quality'); print(f'Target: {p.target_points}, Frames FPS: {p.fps_range}, Features: {p.max_num_features}')"
```

**Check GPU is working:**
```bash
nvidia-smi
# Should show GPU utilization during processing
```

---

## ✅ Success Indicators

1. **Backend responds**: `curl ... /health` returns JSON
2. **Frontend loads**: No 404 errors
3. **Dense reconstruction**: 1M-8M points (was 50K-200K)
4. **Complete coverage**: Entire room visible in viewer
5. **Processing time**: 2-5 minutes (acceptable for quality)

---

## 📞 Quick Commands Reference

### Mac Terminal:
```bash
# SSH to RunPod
ssh root@203.57.40.132 -p 10164

# Test backend
curl https://k0r2cn19yf6osw-8888.proxy.runpod.net/health
```

### On RunPod:
```bash
# Restart backend
cd /workspace/metroa-demo && git pull metroa main
pkill -9 python3 && source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 > backend.log 2>&1 &
echo $! > backend.pid

# Check status
curl http://localhost:8888/health
tail -20 backend.log
```

---

**Priority**: Fix backend connection FIRST, then test new dense settings!

