# Metroa Labs Pipeline Architecture

## Current Pipeline Flow

```
Video Upload
    ↓
/workspace/data/uploads/{scan_id}/video.mp4
    ↓
Frame Extraction (FFmpeg)
    ↓
/workspace/data/results/{scan_id}/images/*.jpg
    ↓
COLMAP Sparse Reconstruction
    ├── Feature Extraction (SIFT)
    ├── Feature Matching
    └── Sparse 3D Reconstruction
    ↓
/workspace/data/results/{scan_id}/sparse/0/
    ├── cameras.bin
    ├── images.bin
    └── points3D.bin
    ↓
COLMAP Dense Reconstruction (if quality >= medium)
    ├── Image Undistortion
    ├── Patch Match Stereo
    └── Stereo Fusion
    ↓
/workspace/data/results/{scan_id}/dense/fused.ply
    ↓
Export to Frontend
```

## Current Quality Modes

- `low`: Basic reconstruction, no dense
- `medium`: Dense reconstruction enabled
- `high`: Enhanced parameters, dense reconstruction
- `ultra`: Maximum parameters, dense reconstruction

## Proposed Enhanced Pipeline

### Quality Mode: `fast`
```
Video → Frames (2-4 fps, 1280-1600px)
    ↓
COLMAP Sparse (8000-10000 features, sequential matching)
    ↓
COLMAP Dense (1600-2000px, moderate iterations)
    ↓
Open3D Post-Processing (light cleanup)
    ↓
pointcloud_final.ply
```

### Quality Mode: `high_quality`
```
Video → Frames (6-8 fps, 1920-3200px)
    ↓
COLMAP Sparse (16384+ features, affine shape, domain pooling)
    ↓
COLMAP Dense (3200-4096px, 10-12 iterations, geom consistency)
    ↓
Open3D Post-Processing (statistical outlier removal, optional downsampling)
    ↓
pointcloud_final.ply
```

### Quality Mode: `ultra_openmvs`
```
Video → Frames (6-8 fps, 1920-3200px)
    ↓
COLMAP Sparse (robust settings for poses)
    ↓
Export to OpenMVS Format
    ↓
OpenMVS DensifyPointCloud
    ↓
OpenMVS ReconstructMesh (optional)
    ↓
Open3D Post-Processing (mandatory cleanup, downsampling if >5M points)
    ↓
pointcloud_final.ply
```

## Data Layout

```
/workspace/data/results/{scan_id}/
├── images/                    # Extracted frames
├── database.db                # COLMAP database
├── sparse/                    # Sparse reconstruction
│   └── 0/
│       ├── cameras.bin
│       ├── images.bin
│       └── points3D.bin
├── dense/                     # Dense reconstruction
│   ├── undistorted/
│   └── fused.ply
├── openmvs/                   # OpenMVS workspace (ultra_openmvs only)
│   ├── scene.mvs
│   └── scene_dense.ply
├── pointcloud_colmap_raw.ply  # Before Open3D
└── pointcloud_final.ply       # After Open3D (final output)
```

## Integration Points

1. **COLMAP Processor** (`colmap_processor.py`)
   - Refactor quality presets into structured config
   - Add OpenMVS export/conversion methods
   - Integrate Open3D post-processing calls

2. **Database** (`database.py`)
   - Add `quality_mode` column to scans table
   - Add `point_count_raw`, `point_count_final` columns
   - Add `postprocessing_stats` JSON field

3. **Main Pipeline** (`main.py`)
   - Update `process_colmap_reconstruction` to handle new modes
   - Add OpenMVS pipeline step for `ultra_openmvs`
   - Add Open3D post-processing step for all modes

4. **Frontend** (`src/app/projects/[id]/page.tsx`)
   - Update quality selector UI
   - Add descriptions for each mode

