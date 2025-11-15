#!/usr/bin/env python3
"""
OpenCV SfM Integration Module

Provides integration functions to use OpenCV SfM alongside COLMAP:
- Quick preview before full COLMAP reconstruction
- Fallback when COLMAP fails
- Comparison and validation tool
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import numpy as np

logger = logging.getLogger(__name__)

try:
    from opencv_sfm import OpenCVSfM, sfm_pipeline, CameraIntrinsics
    HAS_OPENCV_SFM = True
except ImportError:
    HAS_OPENCV_SFM = False
    logger.warning("OpenCV SfM not available")


def run_opencv_preview(
    images_dir: Path,
    output_path: Path,
    max_images: int = 20,
    feature_type: str = "SIFT"
) -> Optional[Tuple[np.ndarray, List]]:
    """
    Run quick OpenCV SfM preview on subset of images
    
    Args:
        images_dir: Directory containing extracted frames
        output_path: Path to save preview PLY file
        max_images: Maximum number of images to process (for speed)
        feature_type: Feature detector type ("SIFT" or "ORB")
    
    Returns:
        Tuple of (3D points, camera poses) or None if failed
    """
    if not HAS_OPENCV_SFM:
        logger.warning("OpenCV SfM not available")
        return None
    
    try:
        # Get image paths (limit for speed)
        image_paths = sorted(list(images_dir.glob("*.jpg")))[:max_images]
        
        if len(image_paths) < 2:
            logger.warning(f"Insufficient images for OpenCV SfM preview: {len(image_paths)}")
            return None
        
        logger.info(f"🔍 Running OpenCV SfM preview on {len(image_paths)} images...")
        
        # Run pipeline
        points_3d, poses = sfm_pipeline(
            image_paths=[str(p) for p in image_paths],
            output_path=str(output_path),
            feature_type=feature_type,
            visualize=False
        )
        
        logger.info(f"✅ OpenCV SfM preview complete: {len(points_3d)} points")
        return points_3d, poses
        
    except Exception as e:
        logger.error(f"OpenCV SfM preview failed: {e}")
        return None


def run_opencv_fallback(
    images_dir: Path,
    output_path: Path,
    feature_type: str = "SIFT"
) -> Optional[Tuple[np.ndarray, List]]:
    """
    Run full OpenCV SfM reconstruction as fallback
    
    Args:
        images_dir: Directory containing extracted frames
        output_path: Path to save PLY file
        feature_type: Feature detector type
    
    Returns:
        Tuple of (3D points, camera poses) or None if failed
    """
    if not HAS_OPENCV_SFM:
        logger.warning("OpenCV SfM not available")
        return None
    
    try:
        # Get all image paths
        image_paths = sorted(list(images_dir.glob("*.jpg")))
        
        if len(image_paths) < 2:
            logger.warning(f"Insufficient images for OpenCV SfM: {len(image_paths)}")
            return None
        
        logger.info(f"🔄 Running OpenCV SfM fallback on {len(image_paths)} images...")
        
        # Run pipeline
        points_3d, poses = sfm_pipeline(
            image_paths=[str(p) for p in image_paths],
            output_path=str(output_path),
            feature_type=feature_type,
            visualize=False
        )
        
        logger.info(f"✅ OpenCV SfM fallback complete: {len(points_3d)} points")
        return points_3d, poses
        
    except Exception as e:
        logger.error(f"OpenCV SfM fallback failed: {e}")
        return None


def compare_reconstructions(
    opencv_ply_path: Path,
    colmap_ply_path: Path
) -> Optional[Dict]:
    """
    Compare OpenCV SfM and COLMAP reconstructions
    
    Args:
        opencv_ply_path: Path to OpenCV SfM PLY file
        colmap_ply_path: Path to COLMAP PLY file
    
    Returns:
        Dictionary with comparison metrics or None if failed
    """
    try:
        from open3d_utils import compare_point_clouds
        
        if not opencv_ply_path.exists():
            logger.warning(f"OpenCV PLY not found: {opencv_ply_path}")
            return None
        
        if not colmap_ply_path.exists():
            logger.warning(f"COLMAP PLY not found: {colmap_ply_path}")
            return None
        
        logger.info("🔍 Comparing OpenCV SfM and COLMAP reconstructions...")
        
        comparison = compare_point_clouds(
            str(opencv_ply_path),
            str(colmap_ply_path),
            visualize=False
        )
        
        logger.info(f"📊 Comparison complete:")
        logger.info(f"   Chamfer distance: {comparison['chamfer_distance']:.6f}")
        logger.info(f"   OpenCV points: {comparison['point_cloud_1']['point_count']:,}")
        logger.info(f"   COLMAP points: {comparison['point_cloud_2']['point_count']:,}")
        
        return comparison
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        return None


def validate_opencv_reconstruction(
    images_dir: Path,
    reference_ply_path: Optional[Path] = None
) -> Dict:
    """
    Validate OpenCV SfM reconstruction quality
    
    Args:
        images_dir: Directory containing images
        reference_ply_path: Optional reference PLY for comparison
    
    Returns:
        Dictionary with validation metrics
    """
    if not HAS_OPENCV_SFM:
        return {"status": "unavailable", "error": "OpenCV SfM not available"}
    
    try:
        # Count images
        image_paths = sorted(list(images_dir.glob("*.jpg")))
        image_count = len(image_paths)
        
        if image_count < 2:
            return {
                "status": "insufficient_images",
                "image_count": image_count,
                "error": "Need at least 2 images"
            }
        
        # Quick test reconstruction
        test_output = images_dir / "validation_test.ply"
        points_3d, poses = run_opencv_preview(
            images_dir,
            test_output,
            max_images=min(10, image_count),
            feature_type="SIFT"
        )
        
        if points_3d is None or len(points_3d) == 0:
            return {
                "status": "failed",
                "error": "Reconstruction produced no points"
            }
        
        # Cleanup test file
        if test_output.exists():
            test_output.unlink()
        
        # Compare with reference if provided
        comparison = None
        if reference_ply_path and reference_ply_path.exists():
            comparison = compare_reconstructions(test_output, reference_ply_path)
        
        return {
            "status": "success",
            "image_count": image_count,
            "point_count": len(points_3d),
            "camera_count": len(poses),
            "comparison": comparison
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

