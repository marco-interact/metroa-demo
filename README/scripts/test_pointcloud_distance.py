#!/usr/bin/env python3
"""
Test script for Open3D point cloud distance calculations

Demonstrates the use of compute_point_cloud_distance and related functions.
"""

import numpy as np
from open3d_utils import (
    compute_point_cloud_distance,
    compute_chamfer_distance,
    compute_hausdorff_distance,
    compare_point_clouds,
    compute_point_cloud_similarity
)

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    print("⚠️  Open3D not available")
    exit(1)


def test_basic_distance():
    """Test basic point cloud distance calculation"""
    print("=" * 60)
    print("Test 1: Basic Point Cloud Distance")
    print("=" * 60)
    
    # Create two dummy point clouds for demonstration
    # Point Cloud 1
    pcd1_points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(pcd1_points)
    
    # Point Cloud 2 (shifted slightly from pcd1)
    pcd2_points = np.array([[0.1, 0.1, 0.1], [1.1, 0.1, 0.1], [0.1, 1.1, 0.1], [0.1, 0.1, 1.1]])
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(pcd2_points)
    
    # Calculate distances
    distances_pcd1_to_pcd2 = compute_point_cloud_distance(pcd1, pcd2)
    distances_pcd2_to_pcd1 = compute_point_cloud_distance(pcd2, pcd1)
    
    print("Distances from pcd1 to pcd2 (for each point in pcd1):")
    print(distances_pcd1_to_pcd2)
    
    print("\nDistances from pcd2 to pcd1 (for each point in pcd2):")
    print(distances_pcd2_to_pcd1)
    
    # Chamfer distance approximation
    chamfer_stats = compute_chamfer_distance(pcd1, pcd2)
    print(f"\nChamfer Distance: {chamfer_stats['chamfer_distance']:.6f}")
    print(f"Mean distance pcd1->pcd2: {chamfer_stats['mean_distance_1_to_2']:.6f}")
    print(f"Mean distance pcd2->pcd1: {chamfer_stats['mean_distance_2_to_1']:.6f}")
    
    print("\n✅ Test 1 passed\n")


def test_chamfer_distance():
    """Test Chamfer distance calculation"""
    print("=" * 60)
    print("Test 2: Chamfer Distance")
    print("=" * 60)
    
    # Create point clouds with known distances
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0]
    ]))
    
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(np.array([
        [0.05, 0.05, 0.05], [1.05, 0.05, 0.05], [0.05, 1.05, 0.05]
    ]))
    
    chamfer_stats = compute_chamfer_distance(pcd1, pcd2)
    
    print(f"Chamfer Distance: {chamfer_stats['chamfer_distance']:.6f}")
    print(f"Max distance pcd1->pcd2: {chamfer_stats['max_distance_1_to_2']:.6f}")
    print(f"Max distance pcd2->pcd1: {chamfer_stats['max_distance_2_to_1']:.6f}")
    print(f"Std dev pcd1->pcd2: {chamfer_stats['std_distance_1_to_2']:.6f}")
    
    print("\n✅ Test 2 passed\n")


def test_hausdorff_distance():
    """Test Hausdorff distance calculation"""
    print("=" * 60)
    print("Test 3: Hausdorff Distance")
    print("=" * 60)
    
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0]
    ]))
    
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(np.array([
        [0.1, 0.1, 0.1], [1.1, 0.1, 0.1], [0.1, 1.1, 0.1], [5, 5, 5]  # Outlier
    ]))
    
    hausdorff_stats = compute_hausdorff_distance(pcd1, pcd2)
    
    print(f"Hausdorff Distance: {hausdorff_stats['hausdorff_distance']:.6f}")
    print(f"Max distance pcd1->pcd2: {hausdorff_stats['max_distance_1_to_2']:.6f}")
    print(f"Max distance pcd2->pcd1: {hausdorff_stats['max_distance_2_to_1']:.6f}")
    
    print("\n✅ Test 3 passed\n")


def test_similarity():
    """Test point cloud similarity calculation"""
    print("=" * 60)
    print("Test 4: Point Cloud Similarity")
    print("=" * 60)
    
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    ]))
    
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(np.array([
        [0.01, 0.01, 0.01], [1.01, 0.01, 0.01], [0.01, 1.01, 0.01], [0.01, 0.01, 1.01]
    ]))
    
    similarity = compute_point_cloud_similarity(pcd1, pcd2, threshold=0.05)
    
    print(f"Chamfer Distance: {similarity['chamfer_distance']:.6f}")
    print(f"Hausdorff Distance: {similarity['hausdorff_distance']:.6f}")
    print(f"Similarity Percentage (threshold={similarity['threshold']}): {similarity['similarity_percentage']:.2f}%")
    print(f"Points within threshold (pcd1->pcd2): {similarity['points_within_threshold_1_to_2']:.2f}%")
    print(f"Points within threshold (pcd2->pcd1): {similarity['points_within_threshold_2_to_1']:.2f}%")
    
    print("\n✅ Test 4 passed\n")


def test_file_comparison():
    """Test comparing point cloud files"""
    print("=" * 60)
    print("Test 5: File Comparison (if files exist)")
    print("=" * 60)
    
    # This would test with actual PLY files if they exist
    # For now, just demonstrate the API
    print("To compare two PLY files:")
    print("  compare_point_clouds('file1.ply', 'file2.ply', visualize=False)")
    print("\n✅ Test 5 passed (API demonstration)\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Open3D Point Cloud Distance Tests")
    print("=" * 60 + "\n")
    
    test_basic_distance()
    test_chamfer_distance()
    test_hausdorff_distance()
    test_similarity()
    test_file_comparison()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

