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
        description="Dense reconstruction for complete room capture",
        estimated_time="2-3 minutes",
        target_points="1M-3M",
        
        # Frame extraction: MORE frames for better coverage
        fps_range=(5, 7),  # Increased significantly for 40s video = 200-280 frames
        max_resolution=2560,  # Higher resolution for better features
        
        # Feature extraction: MUCH more features
        max_num_features=16384,  # Doubled for better matching
        estimate_affine_shape=True,  # Enable for better matching
        domain_size_pooling=True,  # Enable for better features
        
        # Feature matching: HIGH overlap for complete coverage
        matching_strategy="sequential",
        overlap=50,  # Increased significantly for dense matching
        
        # Sparse reconstruction: More points
        min_num_matches=15,  # Lower threshold for more matches
        init_min_num_inliers=100,
        filter_max_reproj_error=4.0,
        
        # Dense reconstruction: MAXIMUM density settings
        enable_dense=True,
        max_image_size=3200,  # Much higher resolution
        window_radius=11,  # Larger window for better stereo matching
        num_samples=30,  # More samples per pixel
        num_iterations=10,  # More iterations for convergence
        geom_consistency_max_cost=0.3,  # Stricter consistency for quality
        filter_min_ncc=0.1,  # Lower threshold for MORE points
        
        # Fusion: RELAXED thresholds for MAXIMUM point density
        fusion_max_reproj_error=2.5,  # Relaxed to include more points
        fusion_max_depth_error=0.02,  # Relaxed
        fusion_max_normal_error=15,  # Relaxed
        fusion_min_num_pixels=2,  # Lower minimum for more points
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: MINIMAL cleanup to preserve density
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=30,
        open3d_statistical_std_ratio=3.0,  # More lenient to keep points
        open3d_downsample_threshold=5000000,  # Only downsample if >5M points
        open3d_voxel_size=0.005,  # Finer voxel size
    ),
    
    "high_quality": QualityPreset(
        name="high_quality",
        description="Maximum density for complete room reconstruction",
        estimated_time="3-5 minutes",
        target_points="3M-8M",
        
        # Frame extraction: MAXIMUM frames for 40s video
        fps_range=(7, 10),  # 280-400 frames for complete coverage
        max_resolution=3200,  # Maximum resolution
        
        # Feature extraction: MAXIMUM features
        max_num_features=16384,  # Maximum SIFT features
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: EXHAUSTIVE for complete coverage
        matching_strategy="exhaustive",  # Changed to exhaustive for maximum matching
        overlap=100,  # Maximum overlap
        
        # Sparse reconstruction: More lenient for MORE points
        min_num_matches=15,  # Lower for more matches
        init_min_num_inliers=100,
        filter_max_reproj_error=3.0,  # More lenient
        
        # Dense reconstruction: ABSOLUTE MAXIMUM settings
        enable_dense=True,
        max_image_size=4096,  # Maximum resolution
        window_radius=13,  # Maximum window size
        num_samples=50,  # Maximum samples
        num_iterations=15,  # Maximum iterations
        geom_consistency_max_cost=0.2,  # Very strict for quality
        filter_min_ncc=0.05,  # Very low threshold for MAXIMUM points
        
        # Fusion: VERY RELAXED for MAXIMUM point density
        fusion_max_reproj_error=3.0,  # Very relaxed
        fusion_max_depth_error=0.03,  # Very relaxed
        fusion_max_normal_error=20,  # Very relaxed
        fusion_min_num_pixels=1,  # Minimum threshold for maximum points
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: MINIMAL cleanup - preserve ALL points
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=40,
        open3d_statistical_std_ratio=3.5,  # Very lenient
        open3d_downsample_threshold=10000000,  # Only downsample if >10M points
        open3d_voxel_size=0.003,  # Very fine voxel size
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

