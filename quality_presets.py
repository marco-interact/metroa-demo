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
        description="High-density reconstruction - Balanced speed & quality",
        estimated_time="3-5 minutes",
        target_points="5M-10M",
        
        # Frame extraction: High frame rate for good coverage
        fps_range=(8, 10),  # 320-400 frames for 40s video
        max_resolution=3200,  # High resolution
        
        # Feature extraction: High feature count
        max_num_features=24576,  # 50% more features
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: Sequential with high overlap
        matching_strategy="sequential",
        overlap=100,  # High overlap for complete coverage
        
        # Sparse reconstruction: Lenient for more points
        min_num_matches=12,  # Very low threshold
        init_min_num_inliers=75,
        filter_max_reproj_error=4.0,  # Lenient
        
        # Dense reconstruction: HIGH density settings
        enable_dense=True,
        max_image_size=4096,  # Very high resolution
        window_radius=13,  # Large window
        num_samples=50,  # High sample count
        num_iterations=15,  # High iteration count
        geom_consistency_max_cost=0.4,  # Lenient for more points
        filter_min_ncc=0.05,  # Low threshold for more points
        
        # Fusion: RELAXED thresholds for high point density
        fusion_max_reproj_error=4.0,  # Very relaxed
        fusion_max_depth_error=0.03,  # Relaxed
        fusion_max_normal_error=20,  # Relaxed
        fusion_min_num_pixels=1,  # Minimum threshold
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: Minimal cleanup to preserve density
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=40,
        open3d_statistical_std_ratio=4.0,  # Very lenient
        open3d_downsample_threshold=20000000,  # Only downsample if >20M points
        open3d_voxel_size=0.002,  # Fine voxel size (2mm)
    ),
    
    "high_quality": QualityPreset(
        name="high_quality",
        description="ULTRA-DENSE reconstruction for complete room capture - Maximum quality",
        estimated_time="5-8 minutes",
        target_points="10M-30M",
        
        # Frame extraction: ABSOLUTE MAXIMUM frames
        fps_range=(10, 15),  # 400-600 frames for 40s video - complete coverage
        max_resolution=3840,  # 4K resolution for maximum detail
        
        # Feature extraction: MAXIMUM SIFT features
        max_num_features=32768,  # DOUBLED - maximum features per image
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: EXHAUSTIVE for complete coverage
        matching_strategy="exhaustive",  # Exhaustive matching - ALL pairs
        overlap=200,  # Super high overlap for dense matching
        
        # Sparse reconstruction: VERY lenient for maximum coverage
        min_num_matches=10,  # Ultra-low threshold for maximum matches
        init_min_num_inliers=50,  # Lower threshold
        filter_max_reproj_error=4.0,  # Very lenient for more points
        
        # Dense reconstruction: ABSOLUTE MAXIMUM settings
        enable_dense=True,
        max_image_size=0,  # 0 = FULL RESOLUTION (no downscaling!)
        window_radius=15,  # Maximum window size for best stereo matching
        num_samples=100,  # DOUBLED samples per pixel for density
        num_iterations=20,  # Maximum iterations for convergence
        geom_consistency_max_cost=0.5,  # More lenient for MORE points
        filter_min_ncc=0.01,  # ULTRA-low threshold - include almost everything
        
        # Fusion: EXTREMELY RELAXED for MAXIMUM point density
        fusion_max_reproj_error=5.0,  # Extremely relaxed
        fusion_max_depth_error=0.05,  # Extremely relaxed
        fusion_max_normal_error=30,  # Extremely relaxed
        fusion_min_num_pixels=1,  # Absolute minimum - maximum points
        
        # OpenMVS: Not used
        use_openmvs=False,
        
        # Open3D: MINIMAL cleanup - preserve EVERYTHING
        open3d_outlier_removal=True,
        open3d_statistical_nb_neighbors=50,
        open3d_statistical_std_ratio=5.0,  # Extremely lenient - keep almost all points
        open3d_downsample_threshold=50000000,  # Only downsample if >50M points
        open3d_voxel_size=0.001,  # Ultra-fine voxel size (1mm)
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

