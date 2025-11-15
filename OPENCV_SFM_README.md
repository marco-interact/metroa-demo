# OpenCV-based Structure from Motion (SfM)

A lightweight SfM implementation using OpenCV for feature detection, matching, camera pose estimation, and triangulation.

## Overview

This module provides an alternative to COLMAP for simpler reconstructions or when a lightweight solution is needed. It implements the core SfM pipeline:

1. **Feature Detection and Matching** - SIFT, SURF, or ORB features
2. **Camera Pose Estimation** - Essential matrix and pose recovery
3. **Triangulation** - 3D point reconstruction from 2D correspondences
4. **Incremental Reconstruction** - Build 3D model incrementally
5. **Visualization and Export** - Open3D visualization and PLY export

## Features

- ✅ Multiple feature detectors (SIFT, SURF, ORB)
- ✅ Robust matching with Lowe's ratio test
- ✅ RANSAC-based outlier rejection
- ✅ Incremental reconstruction
- ✅ Automatic camera intrinsics estimation
- ✅ Point cloud export (PLY format)
- ✅ Open3D visualization

## Usage

### Command Line

```bash
# Basic usage (auto-estimate intrinsics)
python opencv_sfm.py image1.jpg image2.jpg image3.jpg -o output.ply

# With custom intrinsics
python opencv_sfm.py images/*.jpg -o output.ply --fx 1000 --fy 1000 --cx 640 --cy 480

# Using ORB features (faster, less accurate)
python opencv_sfm.py images/*.jpg -o output.ply --feature ORB

# With visualization
python opencv_sfm.py images/*.jpg -o output.ply --visualize
```

### Python API

```python
from opencv_sfm import OpenCVSfM, CameraIntrinsics, sfm_pipeline

# Option 1: High-level pipeline
points_3d, poses = sfm_pipeline(
    image_paths=["img1.jpg", "img2.jpg", "img3.jpg"],
    output_path="output.ply",
    visualize=True
)

# Option 2: Step-by-step control
sfm = OpenCVSfM(feature_type="SIFT")
sfm.load_images(["img1.jpg", "img2.jpg", "img3.jpg"])
sfm.detect_features()
sfm.reconstruct_incremental()
sfm.save_pointcloud("output.ply")
sfm.visualize()
```

## Integration with Metroa

### Use as Alternative to COLMAP

```python
from opencv_sfm import sfm_pipeline
from pathlib import Path

# Reconstruct from extracted frames
frame_dir = Path("/workspace/data/results/scan_id/images")
image_paths = sorted(frame_dir.glob("*.jpg"))

points_3d, poses = sfm_pipeline(
    image_paths=[str(p) for p in image_paths],
    output_path="/workspace/data/results/scan_id/opencv_reconstruction.ply"
)
```

### Comparison with COLMAP

| Feature | OpenCV SfM | COLMAP |
|---------|-----------|--------|
| Speed | ⚡ Fast | 🐌 Slower |
| Accuracy | ✅ Good | ✅ Excellent |
| Point Density | Medium | High |
| Bundle Adjustment | ❌ No | ✅ Yes |
| Dense Reconstruction | ❌ No | ✅ Yes |
| Best For | Quick previews, simple scenes | Production quality |

## Parameters

### Camera Intrinsics

If not provided, intrinsics are auto-estimated from image dimensions:

```python
from opencv_sfm import CameraIntrinsics

# Manual intrinsics
intrinsics = CameraIntrinsics(
    fx=1000.0,  # Focal length X
    fy=1000.0,  # Focal length Y
    cx=640.0,   # Principal point X
    cy=480.0    # Principal point Y
)

# From matrix
K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
intrinsics = CameraIntrinsics.from_matrix(K)

# Default (from image size)
intrinsics = CameraIntrinsics.default(width=1920, height=1080, fov_deg=50.0)
```

### Feature Detectors

- **SIFT** (default): Most accurate, slower
- **SURF**: Fast, good accuracy (requires opencv-contrib)
- **ORB**: Fastest, less accurate, free

### Matching

- **FLANN** (default): Fast approximate matching
- **BF**: Brute force, exact matching

## Limitations

1. **No Bundle Adjustment**: Camera poses and 3D points are not refined
2. **Scale Ambiguity**: Reconstruction scale is arbitrary
3. **No Dense Reconstruction**: Only sparse point cloud
4. **Sequential Processing**: Incremental reconstruction may accumulate errors
5. **Limited Robustness**: Less robust to challenging scenes than COLMAP

## When to Use

✅ **Use OpenCV SfM when:**
- Quick preview needed
- Simple scenes with good overlap
- Lightweight solution required
- Educational purposes
- Integration with existing OpenCV workflows

❌ **Use COLMAP when:**
- Production quality needed
- Challenging scenes (low texture, repetitive patterns)
- Dense reconstruction required
- Maximum accuracy needed
- Large image sets

## Dependencies

- `opencv-python` - Already in requirements.txt
- `numpy` - Already in requirements.txt
- `open3d` - Already in requirements.txt (for visualization)

## Examples

See `opencv_sfm.py` for complete implementation and examples.

## References

- [OpenCV SfM Tutorial](https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html)
- [Multiple View Geometry](https://www.robots.ox.ac.uk/~vgg/hzbook/)
- [COLMAP Documentation](https://colmap.github.io/) (for comparison)

