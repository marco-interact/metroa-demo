#!/usr/bin/env python3
"""
PLY to GLTF/GLB Converter
Converts PLY point clouds to GLTF/GLB format for web viewing
"""

import open3d as o3d
import numpy as np
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import trimesh
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False
    logger.warning("trimesh not available, GLTF export will use Open3D only")


def ply_to_gltf(ply_path: str, output_path: str, format: str = "glb") -> bool:
    """
    Convert PLY point cloud to GLTF/GLB format
    
    Args:
        ply_path: Path to input PLY file
        output_path: Path to output GLTF/GLB file
        format: Output format ("gltf" or "glb")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        ply_path = Path(ply_path)
        output_path = Path(output_path)
        
        if not ply_path.exists():
            logger.error(f"PLY file not found: {ply_path}")
            return False
        
        # Load PLY file with Open3D
        logger.info(f"Loading PLY file: {ply_path}")
        pcd = o3d.io.read_point_cloud(str(ply_path))
        
        if not pcd.has_points():
            logger.error("PLY file contains no points")
            return False
        
        logger.info(f"Loaded {len(pcd.points):,} points")
        
        # Convert to numpy arrays
        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors) if pcd.has_colors() else None
        
        # Use trimesh if available (better GLTF support)
        if HAS_TRIMESH:
            try:
                # Create trimesh point cloud
                if colors is not None:
                    # Normalize colors to 0-255 range if needed
                    if colors.max() <= 1.0:
                        colors = (colors * 255).astype(np.uint8)
                    else:
                        colors = colors.astype(np.uint8)
                    
                    # Create point cloud with colors
                    point_cloud = trimesh.PointCloud(vertices=points, colors=colors)
                else:
                    point_cloud = trimesh.PointCloud(vertices=points)
                
                # Export to GLTF/GLB
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                if format.lower() == "glb":
                    point_cloud.export(str(output_path), file_type='glb')
                else:
                    point_cloud.export(str(output_path), file_type='gltf')
                
                logger.info(f"✅ Exported GLTF to {output_path}")
                return True
                
            except Exception as e:
                logger.warning(f"trimesh export failed: {e}, trying Open3D fallback")
        
        # Fallback: Use Open3D mesh conversion (requires mesh reconstruction)
        # For point clouds, we'll create a simple mesh representation
        logger.info("Using Open3D mesh conversion (point cloud will be converted to mesh)")
        
        # Estimate normals for mesh reconstruction
        pcd.estimate_normals()
        
        # Reconstruct mesh using Poisson surface reconstruction
        try:
            mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
            mesh.remove_degenerate_triangles()
            mesh.remove_duplicated_triangles()
            mesh.remove_duplicated_vertices()
            mesh.remove_non_manifold_edges()
            
            logger.info(f"Created mesh with {len(mesh.vertices):,} vertices")
            
            # Export mesh to GLTF/GLB
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "glb":
                o3d.io.write_triangle_mesh(str(output_path), mesh, write_ascii=False)
            else:
                # Open3D doesn't directly support GLTF, so we'll export as OBJ and convert
                # For now, export as PLY (can be enhanced later)
                logger.warning("Open3D GLTF export not directly supported, exporting as PLY")
                return False
                
        except Exception as e:
            logger.error(f"Mesh reconstruction failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error converting PLY to GLTF: {e}")
        return False


def ply_to_glb(ply_path: str, output_path: str) -> bool:
    """Convenience function for GLB export"""
    return ply_to_gltf(ply_path, output_path, format="glb")


def ply_to_gltf_ascii(ply_path: str, output_path: str) -> bool:
    """Convenience function for GLTF (ASCII) export"""
    return ply_to_gltf(ply_path, output_path, format="gltf")

