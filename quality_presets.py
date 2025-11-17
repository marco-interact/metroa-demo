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
        description="Quick processing with mesh generation",
        estimated_time="60-90 seconds",
        target_points="100K-300K",
        
        # Frame extraction: Optimized for 40s videos
        fps_range=(3, 5),  # Increased from (2, 4) for better coverage
        max_resolution=1920,  # Increased from 1600 for better quality
        
        # Feature extraction: Improved settings
        max_num_features=12000,  # Increased from 10000
        estimate_affine_shape=False,
        domain_size_pooling=False,
        
        # Feature matching: Improved overlap
        matching_strategy="sequential",
        overlap=30,  # Increased from 20 for better matching
        
        # Sparse reconstruction: Balanced settings
        min_num_matches=20,  # Increased from 15
        init_min_num_inliers=120,  # Increased from 100
        filter_max_reproj_error=4.0,  # Reduced from 6.0 for better accuracy
        
        # Dense reconstruction: Improved settings
        enable_dense=True,
        max_image_size=2400,  # Increased from 2000
        window_radius=7,  # Increased from 5
        num_samples=20,  # Increased from 15
        num_iterations=6,  # Increased from 5
        geom_consistency_max_cost=0.8,  # Reduced from 1.0
        filter_min_ncc=0.15,  # Increased from 0.1
        
        # Fusion: Improved thresholds
        fusion_max_reproj_error=1.5,  # Reduced from 2.0
        fusion_max_depth_error=0.012,  # Reduced from 0.015
        fusion_max_normal_error=10,  # Reduced from 12
        fusion_min_num_pixels=3,  # Reduced from 4
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: Moderate cleanup
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=25,  # Increased from 20
        open3d_statistical_std_ratio=2.5,  # Increased from 2.0
        open3d_downsample_threshold=2000000,  # Downsample if >2M points
        open3d_voxel_size=0.008,  # Reduced from 0.01 for finer sampling
    ),
    
    "high_quality": QualityPreset(
        name="high_quality",
        description="High quality reconstruction with mesh generation",
        estimated_time="2-3 minutes",
        target_points="500K-2M",
        
        # Frame extraction: Optimized for 40s videos
        fps_range=(5, 7),  # Reduced from (6, 8) for balance
        max_resolution=2560,  # Reduced from 3200 for performance
        
        # Feature extraction: Enhanced SIFT
        max_num_features=14000,  # Reduced from 16384 for performance
        estimate_affine_shape=True,  # Enable affine shape estimation
        domain_size_pooling=True,     # Enable domain size pooling
        
        # Feature matching: Sequential with high overlap
        matching_strategy="sequential",
        overlap=60,  # Reduced from 100 for performance
        
        # Sparse reconstruction: Balanced settings
        min_num_matches=25,  # Reduced from 30
        init_min_num_inliers=150,  # Reduced from 200
        filter_max_reproj_error=2.5,  # Increased from 2.0 for more points
        
        # Dense reconstruction: Balanced quality settings
        enable_dense=True,
        max_image_size=3200,  # Reduced from 4096
        window_radius=9,  # Reduced from 11
        num_samples=35,  # Reduced from 50
        num_iterations=8,  # Reduced from 10
        geom_consistency_max_cost=0.5,  # Increased from 0.4
        filter_min_ncc=0.25,  # Reduced from 0.3
        
        # Fusion: Balanced for good point density
        fusion_max_reproj_error=1.0,  # Reduced from 1.2
        fusion_max_depth_error=0.008,  # Reduced from 0.01
        fusion_max_normal_error=10,  # Increased from 8
        fusion_min_num_pixels=2,
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: Strong cleanup
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=30,  # Increased from 20
        open3d_statistical_std_ratio=2.0,
        open3d_downsample_threshold=3000000,  # Downsample if >3M points
        open3d_voxel_size=0.004,  # Reduced from 0.005
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

