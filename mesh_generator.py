#!/usr/bin/env python3
"""
Mesh Generation from Point Clouds (OpenMVS-based)
Uses OpenMVS ReconstructMesh for high-quality mesh reconstruction
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


def generate_mesh_from_pointcloud(
    input_ply_path: str,
    output_mesh_path: str,
    method: str = "openmvs",
    decimation_target: Optional[int] = None,
    quality_mode: str = "high_quality"
) -> Dict[str, Any]:
    """
    Generate mesh from point cloud using OpenMVS
    
    Args:
        input_ply_path: Path to input PLY point cloud
        output_mesh_path: Path to save output mesh (OBJ, PLY, or GLB)
        method: Reconstruction method (only "openmvs" supported)
        decimation_target: Target face count for decimation (optional)
        quality_mode: Quality mode (affects resolution and smoothness)
    
    Returns:
        Dictionary with mesh statistics and paths
    """
    try:
        input_path = Path(input_ply_path)
        output_path = Path(output_mesh_path)
        
        if not input_path.exists():
            logger.error(f"Input PLY not found: {input_path}")
            return {"status": "error", "error": "Input file not found"}
        
        if method != "openmvs":
            logger.warning(f"Unsupported method '{method}', using OpenMVS")
        
        # OpenMVS requires MVS format, not PLY
        # This function is meant to be called after OpenMVS densification
        # For now, return error since we should use OpenMVS ReconstructMesh directly
        logger.error("mesh_generator.py should not be used directly. Use OpenMVS ReconstructMesh in the pipeline.")
        return {
            "status": "error",
            "error": "Use OpenMVS ReconstructMesh in openmvs_processor.py instead"
        }
        
    except Exception as e:
        logger.error(f"Error generating mesh: {e}")
        return {"status": "error", "error": str(e)}


def generate_multi_resolution_meshes(
    input_ply_path: str,
    output_dir: Path,
    quality_mode: str = "high_quality"
) -> Dict[str, Any]:
    """
    Generate multiple resolution meshes (deprecated)
    
    Use OpenMVS pipeline instead for consistent mesh generation
    """
    logger.error("Multi-resolution mesh generation is deprecated. Use OpenMVS pipeline.")
    return {
        "status": "error",
        "error": "Deprecated: Use OpenMVS ReconstructMesh with different resolution-level settings"
    }


# Backward compatibility notice
logger.info("⚠️  mesh_generator.py is deprecated. Use openmvs_processor.py for mesh generation.")
