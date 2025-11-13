#!/usr/bin/env python3
"""
Open3D Point Cloud Post-Processing Module

Provides point cloud cleaning, outlier removal, and downsampling
for all reconstruction modes.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    logger.warning("⚠️  Open3D not available. Post-processing will be skipped.")


def postprocess_pointcloud(
    input_ply_path: str,
    output_ply_path: str,
    quality_preset: Optional[Dict] = None,
    progress_callback=None
) -> Dict[str, any]:
    """
    Post-process point cloud using Open3D
    
    Args:
        input_ply_path: Path to input PLY file
        output_ply_path: Path to save cleaned PLY file
        quality_preset: Quality preset configuration (from quality_presets.py)
        progress_callback: Optional callback(current_step, total_steps, message)
    
    Returns:
        Dictionary with stats:
        - point_count_before: int
        - point_count_after: int
        - bounding_box: dict with min/max/extent
        - processing_steps: list of steps performed
    """
    if not OPEN3D_AVAILABLE:
        logger.warning("⚠️  Open3D not available, copying input file as-is")
        import shutil
        shutil.copy(input_ply_path, output_ply_path)
        return {
            "point_count_before": 0,
            "point_count_after": 0,
            "bounding_box": None,
            "processing_steps": ["skipped"],
            "error": "Open3D not available"
        }
    
    input_path = Path(input_ply_path)
    output_path = Path(output_ply_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input PLY file not found: {input_ply_path}")
    
    stats = {
        "point_count_before": 0,
        "point_count_after": 0,
        "bounding_box": None,
        "processing_steps": []
    }
    
    try:
        # Load point cloud
        if progress_callback:
            progress_callback(1, 5, "Loading point cloud...")
        
        pcd = o3d.io.read_point_cloud(str(input_path))
        stats["point_count_before"] = len(pcd.points)
        
        if stats["point_count_before"] == 0:
            raise ValueError(f"Point cloud is empty: {input_path}")
        
        logger.info(f"📊 Loaded {stats['point_count_before']:,} points from {input_path}")
        
        # Default post-processing parameters
        outlier_removal = True
        statistical_nb_neighbors = 20
        statistical_std_ratio = 2.0
        downsample_threshold = 5000000
        voxel_size = 0.005
        
        # Override with quality preset if provided
        if quality_preset:
            outlier_removal = quality_preset.get("open3d_outlier_removal", True)
            statistical_nb_neighbors = quality_preset.get("open3d_statistical_nb_neighbors", 20)
            statistical_std_ratio = quality_preset.get("open3d_statistical_std_ratio", 2.0)
            downsample_threshold = quality_preset.get("open3d_downsample_threshold", 5000000)
            voxel_size = quality_preset.get("open3d_voxel_size", 0.005)
        
        # Step 1: Statistical outlier removal
        if outlier_removal:
            if progress_callback:
                progress_callback(2, 5, "Removing statistical outliers...")
            
            pcd, outlier_indices = pcd.remove_statistical_outlier(
                nb_neighbors=statistical_nb_neighbors,
                std_ratio=statistical_std_ratio
            )
            removed_count = len(outlier_indices)
            stats["processing_steps"].append(f"Removed {removed_count:,} statistical outliers")
            logger.info(f"✅ Removed {removed_count:,} statistical outliers")
        
        # Step 2: Radius-based outlier removal (optional, for very noisy clouds)
        # Skipped for now - statistical removal is usually sufficient
        
        # Step 3: Downsampling if point count exceeds threshold
        if len(pcd.points) > downsample_threshold:
            if progress_callback:
                progress_callback(3, 5, f"Downsampling point cloud ({len(pcd.points):,} points)...")
            
            original_count = len(pcd.points)
            pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
            stats["processing_steps"].append(
                f"Downsampled from {original_count:,} to {len(pcd.points):,} points "
                f"(voxel_size={voxel_size})"
            )
            logger.info(f"✅ Downsampled: {original_count:,} → {len(pcd.points):,} points")
        else:
            if progress_callback:
                progress_callback(3, 5, "Point count within threshold, skipping downsampling")
            stats["processing_steps"].append("Downsampling skipped (within threshold)")
        
        # Step 4: Compute bounding box
        if progress_callback:
            progress_callback(4, 5, "Computing bounding box...")
        
        bbox = pcd.get_axis_aligned_bounding_box()
        bbox_min = bbox.min_bound
        bbox_max = bbox.max_bound
        bbox_extent = bbox_max - bbox_min
        
        stats["bounding_box"] = {
            "min": [float(bbox_min[0]), float(bbox_min[1]), float(bbox_min[2])],
            "max": [float(bbox_max[0]), float(bbox_max[1]), float(bbox_max[2])],
            "extent": [float(bbox_extent[0]), float(bbox_extent[1]), float(bbox_extent[2])],
            "volume": float(bbox_extent[0] * bbox_extent[1] * bbox_extent[2])
        }
        
        # Step 5: Save cleaned point cloud
        if progress_callback:
            progress_callback(5, 5, "Saving cleaned point cloud...")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        success = o3d.io.write_point_cloud(str(output_path), pcd)
        
        if not success:
            raise RuntimeError(f"Failed to save point cloud to {output_path}")
        
        stats["point_count_after"] = len(pcd.points)
        stats["processing_steps"].append(f"Saved to {output_path}")
        
        logger.info(f"✅ Post-processing complete: {stats['point_count_before']:,} → {stats['point_count_after']:,} points")
        logger.info(f"📦 Bounding box: {bbox_extent[0]:.2f} × {bbox_extent[1]:.2f} × {bbox_extent[2]:.2f}")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Post-processing failed: {e}")
        stats["error"] = str(e)
        # Fallback: copy input file
        import shutil
        shutil.copy(input_path, output_path)
        return stats


def get_pointcloud_stats(ply_path: str) -> Dict[str, any]:
    """
    Get statistics about a point cloud file without loading it fully
    
    Returns:
        Dictionary with point count and basic info
    """
    if not OPEN3D_AVAILABLE:
        # Fallback: parse PLY header
        try:
            with open(ply_path, 'rb') as f:
                for _ in range(100):
                    line = f.readline().decode('utf-8', errors='ignore')
                    if 'element vertex' in line.lower():
                        point_count = int(line.split()[-1])
                        return {"point_count": point_count, "method": "header_parsing"}
        except Exception as e:
            logger.warning(f"Could not parse PLY header: {e}")
            return {"point_count": 0, "error": str(e)}
    
    try:
        pcd = o3d.io.read_point_cloud(str(ply_path))
        bbox = pcd.get_axis_aligned_bounding_box()
        bbox_extent = bbox.max_bound - bbox.min_bound
        
        return {
            "point_count": len(pcd.points),
            "bounding_box": {
                "min": bbox.min_bound.tolist(),
                "max": bbox.max_bound.tolist(),
                "extent": bbox_extent.tolist(),
                "volume": float(np.prod(bbox_extent))
            },
            "method": "open3d"
        }
    except Exception as e:
        logger.error(f"Failed to get point cloud stats: {e}")
        return {"point_count": 0, "error": str(e)}

