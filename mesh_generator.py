#!/usr/bin/env python3
"""
Mesh Generation from Point Clouds
Uses Open3D for high-quality mesh reconstruction
"""

import open3d as o3d
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def generate_mesh_from_pointcloud(
    input_ply_path: str,
    output_mesh_path: str,
    method: str = "poisson",
    depth: int = 9,
    decimation_target: Optional[int] = None,
    quality_mode: str = "high_quality"
) -> Dict[str, Any]:
    """
    Generate mesh from point cloud using Open3D
    
    Args:
        input_ply_path: Path to input PLY point cloud
        output_mesh_path: Path to save output mesh (OBJ, PLY, or GLB)
        method: Reconstruction method ("poisson", "ball_pivoting", or "alpha_shape")
        depth: Octree depth for Poisson (higher = more detail, but slower)
        decimation_target: Target triangle count (None = no decimation)
        quality_mode: Quality mode for adaptive parameters
    
    Returns:
        Dictionary with mesh statistics and paths
    """
    try:
        logger.info(f"🔨 Generating mesh from {input_ply_path}")
        logger.info(f"   Method: {method}, Depth: {depth}, Quality: {quality_mode}")
        
        # Load point cloud
        pcd = o3d.io.read_point_cloud(str(input_ply_path))
        
        if not pcd.has_points():
            raise ValueError(f"Point cloud is empty: {input_ply_path}")
        
        point_count = len(pcd.points)
        logger.info(f"📊 Loaded {point_count:,} points")
        
        # Estimate normals if not present
        if not pcd.has_normals():
            logger.info("🧮 Computing normals...")
            # Adaptive normal estimation based on point density
            if quality_mode == "fast":
                radius = 0.05
                max_nn = 20
            elif quality_mode == "high_quality":
                radius = 0.03
                max_nn = 30
            else:  # ultra_openmvs
                radius = 0.02
                max_nn = 50
            
            pcd.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(
                    radius=radius,
                    max_nn=max_nn
                )
            )
            
            # Orient normals consistently
            pcd.orient_normals_consistent_tangent_plane(k=15)
        
        # Generate mesh based on method
        mesh = None
        densities = None
        
        if method == "poisson":
            logger.info(f"🏗️  Running Poisson surface reconstruction (depth={depth})...")
            
            # Adjust depth based on quality mode
            if quality_mode == "fast":
                depth = min(depth, 8)
            elif quality_mode == "high_quality":
                depth = min(depth, 10)
            else:  # ultra_openmvs
                depth = min(depth, 11)
            
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd,
                depth=depth,
                width=0,
                scale=1.1,
                linear_fit=False
            )
            
            # Remove low-density vertices (artifacts)
            if densities is not None:
                logger.info("🧹 Removing low-density artifacts...")
                densities = np.asarray(densities)
                density_threshold = np.quantile(densities, 0.01)  # Remove bottom 1%
                vertices_to_remove = densities < density_threshold
                mesh.remove_vertices_by_mask(vertices_to_remove)
        
        elif method == "ball_pivoting":
            logger.info("🏗️  Running Ball Pivoting algorithm...")
            
            # Estimate appropriate ball radii
            distances = pcd.compute_nearest_neighbor_distance()
            avg_dist = np.mean(distances)
            radii = [avg_dist, avg_dist * 2, avg_dist * 4]
            
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                pcd,
                o3d.utility.DoubleVector(radii)
            )
        
        elif method == "alpha_shape":
            logger.info("🏗️  Running Alpha Shape reconstruction...")
            
            # Estimate alpha parameter
            distances = pcd.compute_nearest_neighbor_distance()
            avg_dist = np.mean(distances)
            alpha = avg_dist * 2
            
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(
                pcd,
                alpha
            )
        
        else:
            raise ValueError(f"Unknown mesh method: {method}")
        
        if mesh is None or len(mesh.vertices) == 0:
            raise RuntimeError(f"Mesh generation failed with method '{method}'")
        
        triangle_count = len(mesh.triangles)
        vertex_count = len(mesh.vertices)
        
        logger.info(f"✅ Mesh generated: {vertex_count:,} vertices, {triangle_count:,} triangles")
        
        # Post-processing
        logger.info("🧹 Cleaning mesh...")
        
        # Remove degenerate triangles
        mesh.remove_degenerate_triangles()
        mesh.remove_duplicated_triangles()
        mesh.remove_duplicated_vertices()
        mesh.remove_non_manifold_edges()
        
        # Decimate if requested
        if decimation_target and triangle_count > decimation_target:
            logger.info(f"🔻 Decimating mesh to {decimation_target:,} triangles...")
            target_ratio = decimation_target / triangle_count
            mesh = mesh.simplify_quadric_decimation(decimation_target)
            logger.info(f"   Reduced to {len(mesh.triangles):,} triangles")
        
        # Compute normals for smooth rendering
        mesh.compute_vertex_normals()
        
        # Save mesh
        output_path = Path(output_mesh_path)
        logger.info(f"💾 Saving mesh to {output_path}")
        
        # Determine format from extension
        ext = output_path.suffix.lower()
        if ext == '.obj':
            o3d.io.write_triangle_mesh(str(output_path), mesh, write_ascii=False)
        elif ext == '.ply':
            o3d.io.write_triangle_mesh(str(output_path), mesh, write_ascii=False)
        elif ext == '.stl':
            o3d.io.write_triangle_mesh(str(output_path), mesh, write_ascii=False)
        elif ext == '.gltf' or ext == '.glb':
            # Export to GLB for web viewing
            o3d.io.write_triangle_mesh(str(output_path), mesh, write_ascii=(ext == '.gltf'))
        else:
            raise ValueError(f"Unsupported mesh format: {ext}")
        
        logger.info(f"✅ Mesh saved successfully")
        
        return {
            "status": "success",
            "mesh_path": str(output_path),
            "method": method,
            "vertices": len(mesh.vertices),
            "triangles": len(mesh.triangles),
            "original_points": point_count,
            "has_vertex_normals": mesh.has_vertex_normals(),
            "has_vertex_colors": mesh.has_vertex_colors(),
            "is_edge_manifold": mesh.is_edge_manifold(),
            "is_vertex_manifold": mesh.is_vertex_manifold(),
            "is_watertight": mesh.is_watertight(),
        }
        
    except Exception as e:
        logger.error(f"❌ Mesh generation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "mesh_path": None
        }


def generate_multi_resolution_meshes(
    input_ply_path: str,
    output_dir: Path,
    quality_mode: str = "high_quality"
) -> Dict[str, Any]:
    """
    Generate multiple resolution meshes for progressive loading
    
    Args:
        input_ply_path: Path to input PLY point cloud
        output_dir: Directory to save meshes
        quality_mode: Quality mode for adaptive parameters
    
    Returns:
        Dictionary with paths to different resolution meshes
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        # High-quality mesh (for download)
        logger.info("📦 Generating high-quality mesh...")
        high_res_result = generate_mesh_from_pointcloud(
            input_ply_path=input_ply_path,
            output_mesh_path=str(output_dir / "mesh_high.obj"),
            method="poisson",
            depth=10,
            decimation_target=None,
            quality_mode=quality_mode
        )
        results["high_quality"] = high_res_result
        
        # Medium-quality mesh (for web viewing)
        logger.info("📦 Generating medium-quality mesh...")
        med_res_result = generate_mesh_from_pointcloud(
            input_ply_path=input_ply_path,
            output_mesh_path=str(output_dir / "mesh_medium.glb"),
            method="poisson",
            depth=9,
            decimation_target=500000,  # 500K triangles
            quality_mode=quality_mode
        )
        results["medium_quality"] = med_res_result
        
        # Low-quality mesh (for preview)
        logger.info("📦 Generating low-quality mesh...")
        low_res_result = generate_mesh_from_pointcloud(
            input_ply_path=input_ply_path,
            output_mesh_path=str(output_dir / "mesh_low.glb"),
            method="poisson",
            depth=8,
            decimation_target=100000,  # 100K triangles
            quality_mode=quality_mode
        )
        results["low_quality"] = low_res_result
        
        logger.info("✅ Multi-resolution meshes generated successfully")
        
        return {
            "status": "success",
            "meshes": results
        }
        
    except Exception as e:
        logger.error(f"❌ Multi-resolution mesh generation failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test mesh generation
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mesh_generator.py <input.ply> [output.obj] [method] [depth]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_mesh.obj"
    method = sys.argv[3] if len(sys.argv) > 3 else "poisson"
    depth = int(sys.argv[4]) if len(sys.argv) > 4 else 9
    
    logging.basicConfig(level=logging.INFO)
    
    result = generate_mesh_from_pointcloud(
        input_ply_path=input_file,
        output_mesh_path=output_file,
        method=method,
        depth=depth
    )
    
    print(f"\n{'='*60}")
    print("Mesh Generation Result:")
    print(f"{'='*60}")
    for key, value in result.items():
        print(f"{key}: {value}")

