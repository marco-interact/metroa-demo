#!/usr/bin/env python3
"""
Open3D Point Cloud Distance Calculation Example

This script demonstrates the exact usage pattern from the user's example,
showing how to use compute_point_cloud_distance for comparing point clouds.
"""

import open3d as o3d
import numpy as np

# Create two dummy point clouds for demonstration
# Point Cloud 1
pcd1_points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
pcd1 = o3d.geometry.PointCloud()
pcd1.points = o3d.utility.Vector3dVector(pcd1_points)

# Point Cloud 2 (shifted slightly from pcd1)
pcd2_points = np.array([[0.1, 0.1, 0.1], [1.1, 0.1, 0.1], [0.1, 1.1, 0.1], [0.1, 0.1, 1.1]])
pcd2 = o3d.geometry.PointCloud()
pcd2.points = o3d.utility.Vector3dVector(pcd2_points)

# Calculate the distance from pcd1 to pcd2
# For each point in pcd1, it finds the closest point in pcd2 and returns that distance
distances_pcd1_to_pcd2 = pcd1.compute_point_cloud_distance(pcd2)
print("Distances from pcd1 to pcd2 (for each point in pcd1):")
print(np.asarray(distances_pcd1_to_pcd2))

# Calculate the distance from pcd2 to pcd1
# For each point in pcd2, it finds the closest point in pcd1 and returns that distance
distances_pcd2_to_pcd1 = pcd2.compute_point_cloud_distance(pcd1)
print("\nDistances from pcd2 to pcd1 (for each point in pcd2):")
print(np.asarray(distances_pcd2_to_pcd1))

# You can also use this to approximate Chamfer distance by averaging distances in both directions
chamfer_distance_approximation = (np.mean(distances_pcd1_to_pcd2) + np.mean(distances_pcd2_to_pcd1)) / 2
print(f"\nApproximate Chamfer Distance: {chamfer_distance_approximation}")

# Visualize the point clouds (optional)
pcd1.paint_uniform_color([1, 0, 0])  # Red for pcd1
pcd2.paint_uniform_color([0, 1, 0])  # Green for pcd2
# Uncomment to visualize:
# o3d.visualization.draw_geometries([pcd1, pcd2])

# Example: Load from PLY files
print("\n" + "=" * 60)
print("Example: Loading from PLY files")
print("=" * 60)

# Example usage with actual files (commented out - uncomment with real paths)
# pcd1 = o3d.io.read_point_cloud("cloud1.ply")
# pcd2 = o3d.io.read_point_cloud("cloud2.ply")
# distances = pcd1.compute_point_cloud_distance(pcd2)
# print(f"Mean distance: {np.mean(distances):.6f}")
# print(f"Max distance: {np.max(distances):.6f}")
# print(f"Min distance: {np.min(distances):.6f}")

print("\n✅ Example complete!")

