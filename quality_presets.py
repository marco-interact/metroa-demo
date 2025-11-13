#!/usr/bin/env python3
"""
Quality Preset Configuration System for Metroa Labs Pipeline

Defines three reconstruction modes:
- fast: Quick processing with conservative settings
- high_quality: Enhanced COLMAP with Open3D cleanup
- ultra_openmvs: COLMAP + OpenMVS + Open3D for maximum quality
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class QualityPreset:
    """Structured quality preset configuration"""
    name: str
    description: str
    estimated_time: str
    target_points: str
    
    # Frame extraction
    fps_range: tuple  # (min, max)
    max_resolution: int  # Long side in pixels
    
    # Feature extraction
    max_num_features: int
    estimate_affine_shape: bool
    domain_size_pooling: bool
    
    # Feature matching
    matching_strategy: str  # "sequential" or "exhaustive"
    overlap: int  # For sequential matching
    
    # Sparse reconstruction
    min_num_matches: int
    init_min_num_inliers: int
    filter_max_reproj_error: float
    
    # Dense reconstruction
    enable_dense: bool
    max_image_size: int  # 0 = full resolution
    window_radius: int
    num_samples: int
    num_iterations: int
    geom_consistency_max_cost: float
    filter_min_ncc: float
    
    # Fusion parameters
    fusion_max_reproj_error: float
    fusion_max_depth_error: float
    fusion_max_normal_error: float
    fusion_min_num_pixels: int
    
    # OpenMVS (ultra_openmvs only)
    use_openmvs: bool
    
    # Open3D post-processing
    open3d_outlier_removal: bool
    open3d_statistical_nb_neighbors: int
    open3d_statistical_std_ratio: float
    open3d_downsample_threshold: int  # Downsample if points > this
    open3d_voxel_size: float  # Voxel size for downsampling


# Quality Preset Definitions
QUALITY_PRESETS: Dict[str, QualityPreset] = {
    "fast": QualityPreset(
        name="fast",
        description="Quick processing, basic point cloud",
        estimated_time="30-60 seconds",
        target_points="50K-200K",
        
        # Frame extraction: Lower FPS, smaller resolution
        fps_range=(2, 4),
        max_resolution=1600,
        
        # Feature extraction: Conservative settings
        max_num_features=10000,
        estimate_affine_shape=False,
        domain_size_pooling=False,
        
        # Feature matching: Sequential with low overlap
        matching_strategy="sequential",
        overlap=20,
        
        # Sparse reconstruction: Faster settings
        min_num_matches=15,
        init_min_num_inliers=100,
        filter_max_reproj_error=6.0,
        
        # Dense reconstruction: Moderate settings
        enable_dense=True,
        max_image_size=2000,
        window_radius=5,
        num_samples=15,
        num_iterations=5,
        geom_consistency_max_cost=1.0,
        filter_min_ncc=0.1,
        
        # Fusion: Conservative thresholds
        fusion_max_reproj_error=2.0,
        fusion_max_depth_error=0.015,
        fusion_max_normal_error=12,
        fusion_min_num_pixels=4,
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: Light cleanup
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=20,
        open3d_statistical_std_ratio=2.0,
        open3d_downsample_threshold=2000000,  # Downsample if >2M points
        open3d_voxel_size=0.01,
    ),
    
    "high_quality": QualityPreset(
        name="high_quality",
        description="High quality reconstruction with enhanced parameters",
        estimated_time="2-4 minutes",
        target_points="1M-5M",
        
        # Frame extraction: Higher FPS, better resolution
        fps_range=(6, 8),
        max_resolution=3200,
        
        # Feature extraction: Enhanced SIFT
        max_num_features=16384,
        estimate_affine_shape=True,  # Enable affine shape estimation
        domain_size_pooling=True,     # Enable domain size pooling
        
        # Feature matching: Sequential with high overlap
        matching_strategy="sequential",
        overlap=100,
        
        # Sparse reconstruction: Stricter settings
        min_num_matches=30,
        init_min_num_inliers=200,
        filter_max_reproj_error=2.0,
        
        # Dense reconstruction: High quality settings
        enable_dense=True,
        max_image_size=4096,
        window_radius=11,
        num_samples=50,
        num_iterations=10,
        geom_consistency_max_cost=0.4,
        filter_min_ncc=0.3,
        
        # Fusion: Slightly relaxed for more points (Open3D will clean)
        fusion_max_reproj_error=1.2,
        fusion_max_depth_error=0.01,
        fusion_max_normal_error=8,
        fusion_min_num_pixels=2,
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: Strong cleanup
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=20,
        open3d_statistical_std_ratio=2.0,
        open3d_downsample_threshold=5000000,  # Downsample if >5M points
        open3d_voxel_size=0.005,
    ),
    
    "ultra_openmvs": QualityPreset(
        name="ultra_openmvs",
        description="Maximum quality with COLMAP + OpenMVS + Open3D",
        estimated_time="4-8 minutes",
        target_points="5M-20M",
        
        # Frame extraction: High FPS, high resolution
        fps_range=(6, 8),
        max_resolution=3200,
        
        # Feature extraction: Maximum features
        max_num_features=16384,  # Focus on robust poses, OpenMVS will densify
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: Sequential (more reliable than exhaustive)
        matching_strategy="sequential",
        overlap=100,
        
        # Sparse reconstruction: Robust settings for poses
        min_num_matches=30,
        init_min_num_inliers=200,
        filter_max_reproj_error=2.0,
        
        # Dense reconstruction: Not used (OpenMVS handles this)
        enable_dense=False,  # OpenMVS will do densification
        max_image_size=0,
        window_radius=0,
        num_samples=0,
        num_iterations=0,
        geom_consistency_max_cost=0.0,
        filter_min_ncc=0.0,
        
        # Fusion: Not used
        fusion_max_reproj_error=0.0,
        fusion_max_depth_error=0.0,
        fusion_max_normal_error=0.0,
        fusion_min_num_pixels=0,
        
        # OpenMVS: Enabled
        use_openmvs=True,
        
        # Open3D: Mandatory cleanup (OpenMVS can produce very dense clouds)
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=20,
        open3d_statistical_std_ratio=2.0,
        open3d_downsample_threshold=5000000,  # Downsample if >5M points
        open3d_voxel_size=0.005,
    ),
}


import logging
logger = logging.getLogger(__name__)

def get_preset(quality_mode: str) -> QualityPreset:
    """Get quality preset by name"""
    if quality_mode not in QUALITY_PRESETS:
        logger.warning(f"Unknown quality mode '{quality_mode}', using 'fast'")
        return QUALITY_PRESETS["fast"]
    return QUALITY_PRESETS[quality_mode]


def map_legacy_quality(legacy_quality: str) -> str:
    """
    Map legacy quality modes to new preset system
    
    Legacy: low, medium, high, ultra
    New: fast, high_quality, ultra_openmvs
    """
    mapping = {
        "low": "fast",
        "medium": "fast",  # Medium maps to fast for now
        "high": "high_quality",
        "ultra": "ultra_openmvs",
    }
    return mapping.get(legacy_quality, "fast")

