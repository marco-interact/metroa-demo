# 🎨 Mesh Generation Integration Guide

## ✅ What's Integrated

Mesh generation is now **fully integrated** into the reconstruction pipeline!

Every reconstruction automatically generates:
1. **Dense Point Cloud** (PLY format) - 1M-8M points
2. **Smooth 3D Mesh** (GLB format) - 300K-1M triangles

---

## 🚀 Deploy to RunPod

### Step 1: SSH into RunPod

```bash
ssh root@203.57.40.132 -p 10164
```

### Step 2: Update Backend

```bash
cd /workspace/metroa-demo

# Pull latest code with mesh generation
git pull metroa main

# Restart backend
kill $(cat backend.pid) 2>/dev/null || true
source venv/bin/activate
QT_QPA_PLATFORM=offscreen nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Verify
curl http://localhost:8888/health
```

---

## 📊 How It Works

### Reconstruction Pipeline

```
Video Upload
    ↓
Frame Extraction (200-400 frames)
    ↓
COLMAP Reconstruction (1M-8M points)
    ↓
Open3D Post-Processing (clean point cloud)
    ↓
🆕 Mesh Generation (Poisson reconstruction)  ← NEW!
    ↓
Save mesh.glb + database update
    ↓
Return URLs for both point cloud & mesh
```

### Mesh Generation Step

```python
# In main.py, after point cloud post-processing:

from mesh_generator import generate_mesh_from_pointcloud

mesh_result = generate_mesh_from_pointcloud(
    input_ply_path=final_ply_path,
    output_mesh_path=results_dir / "mesh.glb",
    method="poisson",
    depth=9,  # Quality-dependent (8-10)
    decimation_target=500000,  # 500K triangles
    quality_mode=quality_mode
)
```

---

## 🎯 Quality Settings

### Fast Mode
- **Mesh Depth**: 8
- **Triangles**: ~300K (decimated)
- **Time**: +20-30 seconds
- **Quality**: Good for preview

### High Quality Mode  
- **Mesh Depth**: 9
- **Triangles**: ~500K (decimated)
- **Time**: +40-60 seconds
- **Quality**: High detail

### Ultra Mode
- **Mesh Depth**: 10
- **Triangles**: ~1M (decimated)
- **Time**: +60-90 seconds
- **Quality**: Maximum detail

---

## 📡 API Endpoints

### Get Mesh File

```bash
GET /api/scans/{scan_id}/mesh

# Returns: GLB file download
# Media Type: model/gltf-binary
```

### Get Scan Details (includes mesh_url)

```bash
GET /api/scans/{scan_id}/details

# Response:
{
  "results": {
    "point_cloud_url": "/results/{scan_id}/pointcloud_final.ply",
    "mesh_url": "/api/scans/{scan_id}/mesh",  ← NEW!
    "thumbnail_url": "..."
  },
  "mesh_triangles": 523145,  ← NEW!
  "mesh_vertices": 261573     ← NEW!
}
```

---

## 🧪 Test Mesh Generation

### 1. Upload a Video

Use the frontend or curl:

```bash
curl -X POST http://localhost:8888/api/reconstruction/upload \
  -F "video=@test_video.mp4" \
  -F "project_id=test-project" \
  -F "scan_name=Mesh Test" \
  -F "quality=high"
```

### 2. Wait for Processing

Monitor logs:

```bash
tail -f /workspace/metroa-demo/backend.log | grep -E "(mesh|Mesh|🔨)"
```

**Expected output:**
```
🔨 Generating mesh from point cloud: /workspace/data/results/.../pointcloud_final.ply
✅ Mesh generated: 261,573 vertices, 523,145 triangles
```

### 3. Download Mesh

```bash
# Get scan ID from processing
SCAN_ID="..."

# Download mesh
curl http://localhost:8888/api/scans/$SCAN_ID/mesh -o test_mesh.glb

# Verify file
file test_mesh.glb
# Should show: glTF binary data
```

### 4. View Mesh

Open `test_mesh.glb` in:
- Blender
- Windows 3D Viewer
- Online GLB viewer: https://gltf-viewer.donmccurdy.com/
- Three.js (in browser)

---

## 🎨 Frontend Integration (Coming Next)

### Add GLB Loader to Simple Viewer

```typescript
import { useGLTF } from '@react-three/drei'

function MeshViewer({ meshUrl }: { meshUrl: string }) {
  const gltf = useGLTF(meshUrl)
  
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} />
      <primitive object={gltf.scene} />
      <OrbitControls />
    </Canvas>
  )
}
```

### Toggle Between Point Cloud & Mesh

```typescript
const [viewMode, setViewMode] = useState<'pointcloud' | 'mesh'>('pointcloud')

{viewMode === 'pointcloud' ? (
  <SimpleViewer modelUrl={pointCloudUrl} />
) : (
  <MeshViewer meshUrl={meshUrl} />
)}
```

---

## 📊 Database Schema

### New Columns in `scans` Table

```sql
ALTER TABLE scans ADD COLUMN mesh_file TEXT;
ALTER TABLE scans ADD COLUMN mesh_triangles INTEGER;
ALTER TABLE scans ADD COLUMN mesh_vertices INTEGER;
```

Automatically created during first reconstruction.

---

## 🐛 Troubleshooting

### Mesh Not Generated

**Check logs:**
```bash
grep -i mesh /workspace/metroa-demo/backend.log
```

**Common issues:**

1. **Point cloud too small** (<10K points)
   - Solution: Use higher quality settings

2. **Open3D not installed**
   - Solution: `pip install open3d==0.19.0`

3. **Mesh generation failed**
   - Check: Point cloud has normals
   - Check: Point cloud not empty
   - Try: Lower mesh depth (8 instead of 9)

### Mesh File Not Found

**Check database:**
```bash
sqlite3 /workspace/database.db "SELECT id, name, mesh_file, mesh_triangles FROM scans WHERE mesh_file IS NOT NULL;"
```

**Check file exists:**
```bash
ls -lh /workspace/data/results/*/mesh.glb
```

### Mesh Too Large

**Increase decimation:**

In `main.py`, line ~440:
```python
decimation_target=300000  # Reduce to 300K triangles
```

---

## ✅ Verification Checklist

- [ ] Backend updated (`git pull metroa main`)
- [ ] Backend restarted
- [ ] Upload test video
- [ ] Check logs for mesh generation
- [ ] Verify mesh file created: `/workspace/data/results/{scan_id}/mesh.glb`
- [ ] Verify database has mesh_file path
- [ ] Download mesh via API: `/api/scans/{scan_id}/mesh`
- [ ] Open mesh in viewer (Blender/online)
- [ ] Verify mesh is smooth and detailed

---

## 📈 Expected Results

### Before (Point Cloud Only)
- ❌ Sparse, disconnected points
- ❌ No smooth surfaces
- ❌ Poor visualization
- ❌ Large file sizes

### After (Point Cloud + Mesh)
- ✅ Dense point cloud (1M-8M points)
- ✅ Smooth mesh surface (300K-1M triangles)
- ✅ Better visualization
- ✅ Optimized file sizes (GLB compression)
- ✅ Web-compatible format

---

## 🎯 Summary

**Mesh generation is now automatic!** Every reconstruction produces:

1. **Point Cloud** (PLY) - For detailed measurements
2. **Mesh** (GLB) - For smooth visualization

**No extra steps needed** - just deploy the updated backend and mesh generation happens automatically during reconstruction.

---

**Status**: ✅ Fully Integrated | ⏳ Awaiting Backend Deployment

