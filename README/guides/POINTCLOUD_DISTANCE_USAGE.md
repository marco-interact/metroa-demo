# Point Cloud Distance Calculation Usage

## Overview

Open3D provides `compute_point_cloud_distance()` for calculating distances between point clouds. This is useful for:
- Comparing reconstructions (before/after processing)
- Validating reconstruction quality
- Comparing different reconstruction methods (COLMAP vs OpenCV SfM)
- Quality assessment and metrics

## Basic Usage

### Direct Open3D Usage

```python
import open3d as o3d
import numpy as np

# Create two point clouds
pcd1_points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
pcd1 = o3d.geometry.PointCloud()
pcd1.points = o3d.utility.Vector3dVector(pcd1_points)

pcd2_points = np.array([[0.1, 0.1, 0.1], [1.1, 0.1, 0.1], [0.1, 1.1, 0.1], [0.1, 0.1, 1.1]])
pcd2 = o3d.geometry.PointCloud()
pcd2.points = o3d.utility.Vector3dVector(pcd2_points)

# Calculate distances
distances_pcd1_to_pcd2 = pcd1.compute_point_cloud_distance(pcd2)
distances_pcd2_to_pcd1 = pcd2.compute_point_cloud_distance(pcd1)

print("Distances from pcd1 to pcd2:", np.asarray(distances_pcd1_to_pcd2))
print("Distances from pcd2 to pcd1:", np.asarray(distances_pcd2_to_pcd1))

# Chamfer distance approximation
chamfer_distance = (np.mean(distances_pcd1_to_pcd2) + np.mean(distances_pcd2_to_pcd1)) / 2
print(f"Chamfer Distance: {chamfer_distance}")
```

### Using Metroa Utilities

```python
from open3d_utils import (
    compute_point_cloud_distance,
    compute_chamfer_distance,
    compute_hausdorff_distance,
    compare_point_clouds
)
import open3d as o3d

# Load point clouds
pcd1 = o3d.io.read_point_cloud("cloud1.ply")
pcd2 = o3d.io.read_point_cloud("cloud2.ply")

# Basic distance
distances = compute_point_cloud_distance(pcd1, pcd2)
print(f"Mean distance: {np.mean(distances):.6f}")

# Chamfer distance (with statistics)
chamfer_stats = compute_chamfer_distance(pcd1, pcd2)
print(f"Chamfer Distance: {chamfer_stats['chamfer_distance']:.6f}")
print(f"Mean 1->2: {chamfer_stats['mean_distance_1_to_2']:.6f}")
print(f"Mean 2->1: {chamfer_stats['mean_distance_2_to_1']:.6f}")

# Hausdorff distance (worst-case)
hausdorff_stats = compute_hausdorff_distance(pcd1, pcd2)
print(f"Hausdorff Distance: {hausdorff_stats['hausdorff_distance']:.6f}")

# File comparison (comprehensive)
comparison = compare_point_clouds("cloud1.ply", "cloud2.ply")
print(f"Chamfer: {comparison['chamfer_distance']:.6f}")
print(f"Point counts: {comparison['point_cloud_1']['point_count']:,} vs {comparison['point_cloud_2']['point_count']:,}")
```

## API Usage

### Compare Two Scans

```bash
curl -X POST http://localhost:8888/api/point-cloud/compare \
  -F "scan_id1=scan-123" \
  -F "scan_id2=scan-456"
```

### Compare Scan with PLY File

```bash
curl -X POST http://localhost:8888/api/point-cloud/compare \
  -F "scan_id1=scan-123" \
  -F "ply_path2=/path/to/reference.ply"
```

### Compare Two PLY Files

```bash
curl -X POST http://localhost:8888/api/point-cloud/compare \
  -F "ply_path1=/path/to/cloud1.ply" \
  -F "ply_path2=/path/to/cloud2.ply"
```

## Integration Examples

### Compare Before/After Post-Processing

```python
from open3d_utils import compare_point_clouds

# Compare raw vs processed
comparison = compare_point_clouds(
    "/workspace/data/results/scan_id/raw.ply",
    "/workspace/data/results/scan_id/processed.ply"
)

print(f"Improvement: Chamfer distance = {comparison['chamfer_distance']:.6f}")
print(f"Points removed: {comparison['point_cloud_1']['point_count'] - comparison['point_cloud_2']['point_count']:,}")
```

### Compare COLMAP vs OpenCV SfM

```python
from opencv_sfm_integration import compare_reconstructions

comparison = compare_reconstructions(
    Path("opencv_reconstruction.ply"),
    Path("colmap_reconstruction.ply")
)

if comparison:
    print(f"Chamfer Distance: {comparison['chamfer_distance']:.6f}")
    print(f"OpenCV points: {comparison['point_cloud_1']['point_count']:,}")
    print(f"COLMAP points: {comparison['point_cloud_2']['point_count']:,}")
```

### Quality Assessment

```python
from open3d_utils import compute_point_cloud_similarity

similarity = compute_point_cloud_similarity(pcd1, pcd2, threshold=0.01)

if similarity['similarity_percentage'] > 95:
    print("✅ Point clouds are very similar")
elif similarity['similarity_percentage'] > 80:
    print("⚠️  Point clouds are moderately similar")
else:
    print("❌ Point clouds differ significantly")
```

## Metrics Explained

### Chamfer Distance
- **Definition**: Average of mean distances in both directions
- **Use**: Overall similarity measure
- **Lower is better**: Smaller = more similar

### Hausdorff Distance
- **Definition**: Maximum of max distances in both directions
- **Use**: Worst-case distance (outlier detection)
- **Lower is better**: Smaller = no large outliers

### Similarity Percentage
- **Definition**: Percentage of points within threshold distance
- **Use**: Quality assessment
- **Higher is better**: Larger = more similar

## Example Scripts

- `example_pointcloud_distance.py` - Basic example matching user's code
- `test_pointcloud_distance.py` - Comprehensive test suite

## References

- [Open3D Documentation](https://www.open3d.org/docs/)
- [Point Cloud Distance API](https://www.open3d.org/docs/release/python_api/open3d.geometry.PointCloud.html#open3d.geometry.PointCloud.compute_point_cloud_distance)

