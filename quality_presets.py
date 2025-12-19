#!/usr/bin/env python3
"""
Quality Preset Configuration System for Metroa Labs Pipeline

Defines three reconstruction modes:
- fast: Quick COLMAP dense reconstruction
- high_quality: Enhanced COLMAP dense with high settings
- ultra_openmvs: COLMAP sparse + OpenMVS densification (maximum quality)

Note: Open3D post-processing has been removed to preserve maximum point cloud density
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


# Quality Preset Definitions
QUALITY_PRESETS: Dict[str, QualityPreset] = {
    "fast": QualityPreset(
        name="fast",
        description="Fast reconstruction with COLMAP dense",
        estimated_time="2-4 minutes",
        target_points="5M-15M",
        
        # Frame extraction: FAST - minimal frames
        fps_range=(6, 10),  # ULTRA OPTIMIZED: Very low FPS for speed
        max_resolution=1920,  # 1080p - balanced quality/speed
        
        # Feature extraction: Balanced features
        max_num_features=16384,  # OPTIMIZED: Reduced from 24576
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: Sequential with minimal overlap for SPEED
        matching_strategy="sequential",
        overlap=30,  # OPTIMIZED: Minimal overlap for fast processing
        
        # Sparse reconstruction: Lenient for more points
        min_num_matches=12,  # Very low threshold
        init_min_num_inliers=75,
        filter_max_reproj_error=4.0,  # Lenient
        
        # Dense reconstruction: FAST settings
        enable_dense=True,
        max_image_size=1920,  # OPTIMIZED: Lower resolution for speed
        window_radius=7,  # OPTIMIZED: Smaller window
        num_samples=20,  # OPTIMIZED: Fewer samples
        num_iterations=7,  # OPTIMIZED: Fewer iterations
        geom_consistency_max_cost=0.4,  # Lenient for more points
        filter_min_ncc=0.05,  # Low threshold for more points
        
        # Fusion: Balanced thresholds
        fusion_max_reproj_error=3.0,  # OPTIMIZED: Reduced from 4.0
        fusion_max_depth_error=0.02,  # OPTIMIZED: Reduced from 0.03
        fusion_max_normal_error=15,  # OPTIMIZED: Reduced from 20
        fusion_min_num_pixels=1,  # Minimum threshold
        
        # OpenMVS: Not used
        use_openmvs=False,
    ),
    
    "high_quality": QualityPreset(
        name="high_quality",
        description="High-quality COLMAP dense reconstruction",
        estimated_time="4-7 minutes",
        target_points="15M-40M",
        
        # Frame extraction: Uses NATIVE video FPS
        fps_range=(24, 30),  # Native FPS (24/30 fps common)
        max_resolution=3840,  # 4K resolution
        
        # Feature extraction: MAXIMUM SIFT features
        max_num_features=32768,  # DOUBLED - maximum features per image
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: Sequential with >80% overlap (UNIFIED)
        matching_strategy="sequential",  # Changed from exhaustive for reliability
        overlap=100,  # UNIFIED: 100 frames for >80% overlap
        
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
    ),
    
    "ultra_openmvs": QualityPreset(
        name="ultra_openmvs",
        description="Maximum density: COLMAP sparse + OpenMVS densification (OPTIMIZED)",
        estimated_time="5-12 minutes",
        target_points="50M-150M+",
        
        # Frame extraction: Uses NATIVE video FPS (OpenMVS densifies)
        fps_range=(24, 30),  # Native FPS - OpenMVS handles density
        max_resolution=3840,  # 4K resolution
        
        # Feature extraction: High features for robust camera poses
        max_num_features=24576,  # INCREASED - more features for better camera tracking
        estimate_affine_shape=True,
        domain_size_pooling=True,
        
        # Feature matching: Sequential with >80% overlap (UNIFIED)
        matching_strategy="sequential",
        overlap=100,  # UNIFIED: 100 frames for >80% overlap
        
        # Sparse reconstruction: Lenient for maximum coverage
        min_num_matches=15,  # LOWERED from 30 - more lenient
        init_min_num_inliers=100,  # LOWERED from 200 - more lenient
        filter_max_reproj_error=3.0,  # INCREASED from 2.0 - more lenient
        
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
        
        # OpenMVS: Enabled - this is where density comes from
        use_openmvs=True,
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

