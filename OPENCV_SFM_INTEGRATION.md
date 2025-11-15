# OpenCV SfM Integration with COLMAP

## Overview

OpenCV SfM has been integrated into the Metroa reconstruction pipeline to work **alongside COLMAP** as a complementary tool. This provides:

1. **Quick Preview** - Fast reconstruction before full COLMAP processing
2. **Fallback Option** - Automatic fallback if COLMAP fails
3. **Comparison Tool** - Validate and compare reconstruction quality
4. **Hybrid Workflow** - Use both methods together for best results

## Integration Points

### 1. Quick Preview (Fast Mode)

When using `quality_mode="fast"`, OpenCV SfM runs a quick preview on the first 20 images before COLMAP starts:

```python
# Automatically runs in process_colmap_reconstruction() when quality_mode="fast"
opencv_preview_path = results_dir / "opencv_preview.ply"
run_opencv_preview(images_dir, opencv_preview_path, max_images=20)
```

**Benefits:**
- ✅ Quick preview (~30-60 seconds)
- ✅ Early validation of reconstruction feasibility
- ✅ User can see results faster
- ✅ Non-blocking (runs in parallel with COLMAP setup)

### 2. Automatic Fallback

If COLMAP reconstruction fails, OpenCV SfM automatically attempts a fallback reconstruction:

```python
# In exception handler of process_colmap_reconstruction()
if COLMAP fails:
    run_opencv_fallback(images_dir, fallback_ply_path)
    # Updates database with OpenCV result
    # Sets quality_mode='opencv_fallback'
```

**Benefits:**
- ✅ Graceful degradation
- ✅ Always produces some result
- ✅ Better user experience
- ✅ Useful for challenging scenes

### 3. Quality Comparison

After COLMAP completes, the system compares OpenCV preview with COLMAP result:

```python
comparison = compare_reconstructions(opencv_preview_path, colmap_ply_path)
# Returns Chamfer distance, point counts, statistics
```

**Benefits:**
- ✅ Quality validation
- ✅ Performance metrics
- ✅ Debugging tool
- ✅ Quality assurance

## Usage

### Automatic (Integrated)

The integration is **automatic** - no code changes needed:

1. **Fast Mode**: OpenCV preview runs automatically
2. **COLMAP Failure**: OpenCV fallback runs automatically
3. **Comparison**: Comparison runs automatically if preview exists

### Manual API

You can also use the integration functions directly:

```python
from opencv_sfm_integration import (
    run_opencv_preview,
    run_opencv_fallback,
    compare_reconstructions,
    validate_opencv_reconstruction
)

# Quick preview
result = run_opencv_preview(
    images_dir=Path("/workspace/data/results/scan_id/images"),
    output_path=Path("/workspace/data/results/scan_id/preview.ply"),
    max_images=20
)

# Fallback reconstruction
result = run_opencv_fallback(
    images_dir=Path("/workspace/data/results/scan_id/images"),
    output_path=Path("/workspace/data/results/scan_id/fallback.ply")
)

# Compare reconstructions
comparison = compare_reconstructions(
    opencv_ply_path=Path("opencv.ply"),
    colmap_ply_path=Path("colmap.ply")
)
```

## Workflow

### Standard Workflow (Fast Mode)

```
1. Extract frames from video
2. Run OpenCV SfM preview (20 images, ~30s) ← NEW
   └─> Saves: opencv_preview.ply
3. Run COLMAP reconstruction (all images, ~2-5min)
   └─> Saves: pointcloud_final.ply
4. Compare OpenCV vs COLMAP ← NEW
   └─> Logs comparison metrics
5. Return COLMAP result (or OpenCV if COLMAP fails)
```

### Fallback Workflow

```
1. Extract frames from video
2. Run COLMAP reconstruction
3. COLMAP fails ❌
4. Run OpenCV SfM fallback ← NEW
   └─> Saves: opencv_fallback.ply
5. Update database with OpenCV result
6. Return OpenCV result ✅
```

## Quality Modes

| Mode | OpenCV Preview | COLMAP | Fallback |
|------|---------------|--------|----------|
| `fast` | ✅ Yes (20 images) | ✅ Yes | ✅ Yes |
| `high_quality` | ❌ No | ✅ Yes | ✅ Yes |
| `ultra_openmvs` | ❌ No | ✅ Yes | ✅ Yes |

## Performance

### OpenCV SfM Preview
- **Time**: ~30-60 seconds (20 images)
- **Points**: 10K-50K (sparse)
- **Use Case**: Quick validation

### COLMAP Reconstruction
- **Time**: 2-10 minutes (all images)
- **Points**: 100K-5M (dense)
- **Use Case**: Production quality

### Comparison
- **Time**: ~5-10 seconds
- **Metrics**: Chamfer distance, point counts, percentiles
- **Use Case**: Quality validation

## Database Integration

OpenCV fallback results are stored in the database:

```sql
UPDATE scans SET 
    status = 'completed',
    ply_file = 'opencv_fallback.ply',
    point_count_raw = <count>,
    quality_mode = 'opencv_fallback'
WHERE id = <scan_id>
```

## Files Created

- `opencv_preview.ply` - Quick preview (fast mode only)
- `opencv_fallback.ply` - Fallback reconstruction (if COLMAP fails)

## Benefits

1. **Faster Feedback** - Users see results sooner
2. **Better Reliability** - Always produces some result
3. **Quality Assurance** - Automatic comparison and validation
4. **Flexibility** - Multiple reconstruction options
5. **Debugging** - Easier to identify issues

## Limitations

- OpenCV SfM produces **sparse** point clouds (no dense reconstruction)
- No bundle adjustment (less accurate than COLMAP)
- Scale ambiguity (arbitrary scale)
- Sequential processing (may accumulate errors)

## When to Use

✅ **OpenCV SfM Preview**: Quick validation, fast mode
✅ **OpenCV SfM Fallback**: COLMAP fails, lightweight needs
❌ **COLMAP**: Production quality, dense reconstruction needed

## Configuration

OpenCV SfM integration is controlled by:

- `HAS_OPENCV_SFM` - Availability check
- `quality_mode` - Determines if preview runs
- Exception handling - Triggers fallback

No additional configuration needed - it's fully integrated!

