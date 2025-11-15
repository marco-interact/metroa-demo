#!/usr/bin/env python3
"""
Open3D Enhanced Utilities

Additional utility functions leveraging Open3D capabilities beyond
basic point cloud post-processing.

Based on Open3D: https://github.com/isl-org/Open3D
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import numpy as np

logger = logging.getLogger(__name__)

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    logger.warning("⚠️  Open3D not available. Enhanced utilities will be disabled.")


def estimate_normals(
    pcd: 'o3d.geometry.PointCloud',
    radius: float = 0.1,
    max_nn: int = 30
) -> 'o3d.geometry.PointCloud':
    """
    Estimate normals for a point cloud
    
    Args:
        pcd: Open3D point cloud
        radius: Search radius for normal estimation
        max_nn: Maximum number of neighbors
    
    Returns:
        Point cloud with estimated normals
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn)
    )
    return pcd


def radius_outlier_removal(
    pcd: 'o3d.geometry.PointCloud',
    nb_points: int = 16,
    radius: float = 0.05
) -> Tuple['o3d.geometry.PointCloud', np.ndarray]:
    """
    Remove outliers using radius-based method
    
    Args:
        pcd: Open3D point cloud
        nb_points: Minimum number of points within radius
        radius: Search radius
    
    Returns:
        Tuple of (cleaned point cloud, outlier indices)
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    pcd_clean, outlier_indices = pcd.remove_radius_outlier(
        nb_points=nb_points,
        radius=radius
    )
    return pcd_clean, outlier_indices


def poisson_surface_reconstruction(
    pcd: 'o3d.geometry.PointCloud',
    depth: int = 9,
    width: int = 0,
    scale: float = 1.1,
    linear_fit: bool = False
) -> Tuple['o3d.geometry.TriangleMesh', np.ndarray]:
    """
    Generate mesh from point cloud using Poisson surface reconstruction
    
    Args:
        pcd: Point cloud with normals
        depth: Octree depth (higher = more detail, slower)
        width: Width parameter (0 = auto)
        scale: Scale parameter
        linear_fit: Use linear interpolation
    
    Returns:
        Tuple of (mesh, densities)
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    if not pcd.has_normals():
        logger.warning("Point cloud has no normals, estimating...")
        pcd = estimate_normals(pcd)
    
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd,
        depth=depth,
        width=width,
        scale=scale,
        linear_fit=linear_fit
    )
    return mesh, densities


def alpha_shape_mesh(
    pcd: 'o3d.geometry.PointCloud',
    alpha: float = 0.03
) -> 'o3d.geometry.TriangleMesh':
    """
    Generate mesh from point cloud using Alpha shapes
    
    Args:
        pcd: Point cloud
        alpha: Alpha parameter (smaller = tighter fit)
    
    Returns:
        Triangle mesh
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
        pcd,
        alpha=alpha
    )
    return mesh


def mesh_simplification(
    mesh: 'o3d.geometry.TriangleMesh',
    target_triangles: int = 10000
) -> 'o3d.geometry.TriangleMesh':
    """
    Simplify mesh by reducing triangle count
    
    Args:
        mesh: Input mesh
        target_triangles: Target number of triangles
    
    Returns:
        Simplified mesh
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    mesh_simplified = mesh.simplify_quadric_decimation(
        target_number_of_triangles=target_triangles
    )
    return mesh_simplified


def icp_registration(
    source: 'o3d.geometry.PointCloud',
    target: 'o3d.geometry.PointCloud',
    max_distance: float = 0.02,
    init_transform: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, Dict]:
    """
    Align two point clouds using Iterative Closest Point (ICP)
    
    Args:
        source: Source point cloud
        target: Target point cloud
        max_distance: Maximum correspondence distance
        init_transform: Initial transformation matrix (4x4)
    
    Returns:
        Tuple of (transformation matrix, registration info)
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    if init_transform is None:
        init_transform = np.eye(4)
    
    result = o3d.pipelines.registration.registration_icp(
        source, target,
        max_correspondence_distance=max_distance,
        init=init_transform,
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint()
    )
    
    return result.transformation, {
        "fitness": result.fitness,
        "inlier_rmse": result.inlier_rmse,
        "correspondence_set": len(result.correspondence_set)
    }


def plane_segmentation(
    pcd: 'o3d.geometry.PointCloud',
    distance_threshold: float = 0.01,
    ransac_n: int = 3,
    num_iterations: int = 1000
) -> Tuple[np.ndarray, List]:
    """
    Segment largest plane from point cloud using RANSAC
    
    Args:
        pcd: Point cloud
        distance_threshold: Distance threshold for plane fitting
        ransac_n: Number of points to sample
        num_iterations: RANSAC iterations
    
    Returns:
        Tuple of (plane inlier indices, plane equation [a, b, c, d])
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    plane_model, inliers = pcd.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations
    )
    
    return inliers, plane_model


def compute_fpfh_features(
    pcd: 'o3d.geometry.PointCloud',
    radius_normal: float = 0.1,
    radius_feature: float = 0.25
) -> 'o3d.pipelines.registration.Feature':
    """
    Compute Fast Point Feature Histograms (FPFH) for point cloud
    
    Args:
        pcd: Point cloud with normals
        radius_normal: Radius for normal estimation
        radius_feature: Radius for feature computation
    
    Returns:
        FPFH feature descriptors
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    if not pcd.has_normals():
        pcd = estimate_normals(pcd, radius=radius_normal)
    
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
    )
    
    return pcd_fpfh


def headless_render(
    mesh: 'o3d.geometry.TriangleMesh',
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    camera_position: Optional[np.ndarray] = None
) -> bool:
    """
    Render mesh to image file (headless, no display required)
    
    Args:
        mesh: Mesh to render
        output_path: Output image path
        width: Image width
        height: Image height
        camera_position: Camera position [x, y, z] (None = auto)
    
    Returns:
        Success status
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False, width=width, height=height)
    vis.add_geometry(mesh)
    
    if camera_position is not None:
        ctr = vis.get_view_control()
        ctr.set_lookat([0, 0, 0])
        ctr.set_up([0, 1, 0])
        ctr.set_front(camera_position)
    
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(output_path)
    vis.destroy_window()
    
    return Path(output_path).exists()


def get_pointcloud_info(pcd: 'o3d.geometry.PointCloud') -> Dict:
    """
    Get comprehensive information about a point cloud
    
    Args:
        pcd: Point cloud
    
    Returns:
        Dictionary with point cloud statistics
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    bbox = pcd.get_axis_aligned_bounding_box()
    bbox_extent = bbox.max_bound - bbox.min_bound
    
    info = {
        "point_count": len(pcd.points),
        "has_normals": pcd.has_normals(),
        "has_colors": pcd.has_colors(),
        "bounding_box": {
            "min": bbox.min_bound.tolist(),
            "max": bbox.max_bound.tolist(),
            "extent": bbox_extent.tolist(),
            "volume": float(np.prod(bbox_extent)),
            "center": bbox.get_center().tolist()
        }
    }
    
    if pcd.has_normals():
        normals = np.asarray(pcd.normals)
        info["normals"] = {
            "mean": normals.mean(axis=0).tolist(),
            "std": normals.std(axis=0).tolist()
        }
    
    return info


def compute_point_cloud_distance(
    source: 'o3d.geometry.PointCloud',
    target: 'o3d.geometry.PointCloud'
) -> np.ndarray:
    """
    Calculate distance from each point in source to nearest point in target
    
    For each point in source, finds the closest point in target and returns
    the Euclidean distance.
    
    Args:
        source: Source point cloud
        target: Target point cloud
    
    Returns:
        Array of distances (one per point in source)
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    distances = source.compute_point_cloud_distance(target)
    return np.asarray(distances)


def compute_chamfer_distance(
    pcd1: 'o3d.geometry.PointCloud',
    pcd2: 'o3d.geometry.PointCloud'
) -> Dict[str, float]:
    """
    Compute Chamfer distance between two point clouds
    
    Chamfer distance is the average of:
    - Mean distance from pcd1 to pcd2
    - Mean distance from pcd2 to pcd1
    
    This provides a symmetric measure of similarity between point clouds.
    
    Args:
        pcd1: First point cloud
        pcd2: Second point cloud
    
    Returns:
        Dictionary with:
        - chamfer_distance: Symmetric Chamfer distance
        - mean_distance_1_to_2: Mean distance from pcd1 to pcd2
        - mean_distance_2_to_1: Mean distance from pcd2 to pcd1
        - max_distance_1_to_2: Max distance from pcd1 to pcd2
        - max_distance_2_to_1: Max distance from pcd2 to pcd1
        - std_distance_1_to_2: Std dev of distances from pcd1 to pcd2
        - std_distance_2_to_1: Std dev of distances from pcd2 to pcd1
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    # Compute distances in both directions
    distances_1_to_2 = compute_point_cloud_distance(pcd1, pcd2)
    distances_2_to_1 = compute_point_cloud_distance(pcd2, pcd1)
    
    # Calculate statistics
    mean_1_to_2 = float(np.mean(distances_1_to_2))
    mean_2_to_1 = float(np.mean(distances_2_to_1))
    max_1_to_2 = float(np.max(distances_1_to_2))
    max_2_to_1 = float(np.max(distances_2_to_1))
    std_1_to_2 = float(np.std(distances_1_to_2))
    std_2_to_1 = float(np.std(distances_2_to_1))
    
    # Chamfer distance (symmetric)
    chamfer_distance = (mean_1_to_2 + mean_2_to_1) / 2.0
    
    return {
        "chamfer_distance": chamfer_distance,
        "mean_distance_1_to_2": mean_1_to_2,
        "mean_distance_2_to_1": mean_2_to_1,
        "max_distance_1_to_2": max_1_to_2,
        "max_distance_2_to_1": max_2_to_1,
        "std_distance_1_to_2": std_1_to_2,
        "std_distance_2_to_1": std_2_to_1
    }


def compare_point_clouds(
    pcd1_path: str,
    pcd2_path: str,
    visualize: bool = False
) -> Dict:
    """
    Compare two point cloud files and compute distance metrics
    
    Args:
        pcd1_path: Path to first point cloud file
        pcd2_path: Path to second point cloud file
        visualize: Whether to visualize the comparison
    
    Returns:
        Dictionary with comparison metrics and statistics
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    # Load point clouds
    pcd1 = o3d.io.read_point_cloud(str(pcd1_path))
    pcd2 = o3d.io.read_point_cloud(str(pcd2_path))
    
    if not pcd1.has_points():
        raise ValueError(f"Point cloud 1 is empty: {pcd1_path}")
    if not pcd2.has_points():
        raise ValueError(f"Point cloud 2 is empty: {pcd2_path}")
    
    # Get basic info
    info1 = get_pointcloud_info(pcd1)
    info2 = get_pointcloud_info(pcd2)
    
    # Compute Chamfer distance
    chamfer_stats = compute_chamfer_distance(pcd1, pcd2)
    
    # Compute individual distances
    distances_1_to_2 = compute_point_cloud_distance(pcd1, pcd2)
    distances_2_to_1 = compute_point_cloud_distance(pcd2, pcd1)
    
    # Percentiles for distance distribution
    percentiles = [50, 75, 90, 95, 99]
    percentiles_1_to_2 = {f"p{p}": float(np.percentile(distances_1_to_2, p)) for p in percentiles}
    percentiles_2_to_1 = {f"p{p}": float(np.percentile(distances_2_to_1, p)) for p in percentiles}
    
    result = {
        "point_cloud_1": {
            "path": str(pcd1_path),
            "point_count": info1["point_count"],
            "bounding_box": info1["bounding_box"]
        },
        "point_cloud_2": {
            "path": str(pcd2_path),
            "point_count": info2["point_count"],
            "bounding_box": info2["bounding_box"]
        },
        "chamfer_distance": chamfer_stats["chamfer_distance"],
        "distance_statistics": {
            "1_to_2": {
                "mean": chamfer_stats["mean_distance_1_to_2"],
                "max": chamfer_stats["max_distance_1_to_2"],
                "std": chamfer_stats["std_distance_1_to_2"],
                "percentiles": percentiles_1_to_2
            },
            "2_to_1": {
                "mean": chamfer_stats["mean_distance_2_to_1"],
                "max": chamfer_stats["max_distance_2_to_1"],
                "std": chamfer_stats["std_distance_2_to_1"],
                "percentiles": percentiles_2_to_1
            }
        }
    }
    
    # Visualize if requested
    if visualize:
        pcd1.paint_uniform_color([1, 0, 0])  # Red
        pcd2.paint_uniform_color([0, 1, 0])  # Green
        o3d.visualization.draw_geometries([pcd1, pcd2])
    
    return result


def compute_hausdorff_distance(
    pcd1: 'o3d.geometry.PointCloud',
    pcd2: 'o3d.geometry.PointCloud'
) -> Dict[str, float]:
    """
    Compute Hausdorff distance between two point clouds
    
    Hausdorff distance is the maximum of:
    - Maximum distance from pcd1 to pcd2
    - Maximum distance from pcd2 to pcd1
    
    This measures the worst-case distance between point clouds.
    
    Args:
        pcd1: First point cloud
        pcd2: Second point cloud
    
    Returns:
        Dictionary with Hausdorff distance and components
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    distances_1_to_2 = compute_point_cloud_distance(pcd1, pcd2)
    distances_2_to_1 = compute_point_cloud_distance(pcd2, pcd1)
    
    max_1_to_2 = float(np.max(distances_1_to_2))
    max_2_to_1 = float(np.max(distances_2_to_1))
    hausdorff_distance = max(max_1_to_2, max_2_to_1)
    
    return {
        "hausdorff_distance": hausdorff_distance,
        "max_distance_1_to_2": max_1_to_2,
        "max_distance_2_to_1": max_2_to_1
    }


def compute_point_cloud_similarity(
    pcd1: 'o3d.geometry.PointCloud',
    pcd2: 'o3d.geometry.PointCloud',
    threshold: float = 0.01
) -> Dict[str, float]:
    """
    Compute similarity metrics between two point clouds
    
    Calculates various metrics including:
    - Chamfer distance
    - Hausdorff distance
    - Percentage of points within threshold
    
    Args:
        pcd1: First point cloud
        pcd2: Second point cloud
        threshold: Distance threshold for similarity percentage
    
    Returns:
        Dictionary with similarity metrics
    """
    if not OPEN3D_AVAILABLE:
        raise RuntimeError("Open3D not available")
    
    # Compute distances
    distances_1_to_2 = compute_point_cloud_distance(pcd1, pcd2)
    distances_2_to_1 = compute_point_cloud_distance(pcd2, pcd1)
    
    # Chamfer distance
    chamfer_stats = compute_chamfer_distance(pcd1, pcd2)
    
    # Hausdorff distance
    hausdorff_stats = compute_hausdorff_distance(pcd1, pcd2)
    
    # Percentage of points within threshold
    within_threshold_1_to_2 = float(np.sum(distances_1_to_2 <= threshold) / len(distances_1_to_2) * 100)
    within_threshold_2_to_1 = float(np.sum(distances_2_to_1 <= threshold) / len(distances_2_to_1) * 100)
    avg_within_threshold = (within_threshold_1_to_2 + within_threshold_2_to_1) / 2.0
    
    return {
        "chamfer_distance": chamfer_stats["chamfer_distance"],
        "hausdorff_distance": hausdorff_stats["hausdorff_distance"],
        "mean_distance": chamfer_stats["chamfer_distance"],
        "max_distance": hausdorff_stats["hausdorff_distance"],
        "similarity_percentage": avg_within_threshold,
        "points_within_threshold_1_to_2": within_threshold_1_to_2,
        "points_within_threshold_2_to_1": within_threshold_2_to_1,
        "threshold": threshold
    }

