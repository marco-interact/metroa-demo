#!/usr/bin/env python3
"""
PLY to GLTF/GLB Converter (Trimesh-based, no Open3D)
Converts PLY point clouds to GLTF/GLB format for web viewing
"""

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
    logger.warning("trimesh not available, GLTF export will not work")


def ply_to_gltf_trimesh(ply_path: str, output_path: str, format: str = "glb") -> bool:
    """
    Convert PLY point cloud to GLTF/GLB format using trimesh
    
    Args:
        ply_path: Path to input PLY file
        output_path: Path to output GLTF/GLB file
        format: Output format ("gltf" or "glb")
    
    Returns:
        True if successful, False otherwise
    """
    if not HAS_TRIMESH:
        logger.error("trimesh is required for GLTF export. Install with: pip install trimesh")
        return False
    
    try:
        ply_path = Path(ply_path)
        output_path = Path(output_path)
        
        if not ply_path.exists():
            logger.error(f"PLY file not found: {ply_path}")
            return False
        
        # Load PLY file with trimesh
        logger.info(f"Loading PLY file: {ply_path}")
        try:
            mesh = trimesh.load(str(ply_path))
        except Exception as e:
            logger.error(f"Failed to load PLY with trimesh: {e}")
            return False
        
        # Check if it's a point cloud or mesh
        if isinstance(mesh, trimesh.PointCloud):
            logger.info(f"Loaded {len(mesh.vertices):,} points")
        elif isinstance(mesh, trimesh.Trimesh):
            logger.info(f"Loaded mesh with {len(mesh.vertices):,} vertices, {len(mesh.faces):,} faces")
        else:
            logger.error(f"Unsupported geometry type: {type(mesh)}")
            return False
        
        # Export to GLTF/GLB
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "glb":
            mesh.export(str(output_path), file_type='glb')
        else:
            mesh.export(str(output_path), file_type='gltf')
        
        logger.info(f"✅ Exported {format.upper()} to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting PLY to GLTF: {e}")
        return False


def ply_to_glb(ply_path: str, output_path: str) -> bool:
    """Convenience function for GLB export"""
    return ply_to_gltf_trimesh(ply_path, output_path, format="glb")


def ply_to_gltf_ascii(ply_path: str, output_path: str) -> bool:
    """Convenience function for GLTF (ASCII) export"""
    return ply_to_gltf_trimesh(ply_path, output_path, format="gltf")


# Backward compatibility aliases
ply_to_gltf = ply_to_gltf_trimesh


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        ply_file = sys.argv[1]
        output_file = sys.argv[2]
        fmt = "glb" if output_file.endswith(".glb") else "gltf"
        success = ply_to_gltf_trimesh(ply_file, output_file, format=fmt)
        if success:
            print(f"✅ Converted {ply_file} to {output_file}")
        else:
            print(f"❌ Failed to convert {ply_file}")
    else:
        print("Usage: python ply_to_gltf.py <input.ply> <output.glb|gltf>")
