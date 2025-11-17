#!/usr/bin/env python3
"""
Optimized 360° Video Handler
Efficiently converts 360° equirectangular videos to perspective frames for COLMAP
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import subprocess
import tempfile

logger = logging.getLogger(__name__)


def generate_optimal_camera_positions(
    num_views: int = 12,
    fov: float = 90.0,
    include_vertical: bool = True
) -> List[Tuple[float, float, float]]:
    """
    Generate optimal camera positions (yaw, pitch, roll) for 360° video coverage
    
    Args:
        num_views: Number of perspective views to extract
        fov: Field of view in degrees
        include_vertical: Include up/down views
    
    Returns:
        List of (yaw, pitch, roll) tuples in degrees
    """
    positions = []
    
    # Horizontal ring (main views)
    num_horizontal = num_views if not include_vertical else num_views - 2
    for i in range(num_horizontal):
        yaw = (360.0 / num_horizontal) * i
        pitch = 0.0  # Level horizon
        roll = 0.0
        positions.append((yaw, pitch, roll))
    
    # Add vertical views for better coverage
    if include_vertical:
        positions.append((0.0, 45.0, 0.0))   # Look up
        positions.append((0.0, -45.0, 0.0))  # Look down
    
    return positions


def equirect_to_perspective_fast(
    equirect_frame: np.ndarray,
    yaw: float,
    pitch: float,
    roll: float,
    fov: float,
    output_size: Tuple[int, int]
) -> np.ndarray:
    """
    Fast conversion from equirectangular to perspective using cv2.remap
    
    Args:
        equirect_frame: Input equirectangular frame
        yaw: Horizontal rotation in degrees
        pitch: Vertical rotation in degrees
        roll: Roll rotation in degrees
        fov: Field of view in degrees
        output_size: (width, height) of output frame
    
    Returns:
        Perspective projected frame
    """
    height_eq, width_eq = equirect_frame.shape[:2]
    width_out, height_out = output_size
    
    # Convert angles to radians
    yaw_rad = np.radians(yaw)
    pitch_rad = np.radians(pitch)
    roll_rad = np.radians(roll)
    fov_rad = np.radians(fov)
    
    # Build rotation matrix
    # Yaw (Y-axis)
    R_yaw = np.array([
        [np.cos(yaw_rad), 0, np.sin(yaw_rad)],
        [0, 1, 0],
        [-np.sin(yaw_rad), 0, np.cos(yaw_rad)]
    ])
    
    # Pitch (X-axis)
    R_pitch = np.array([
        [1, 0, 0],
        [0, np.cos(pitch_rad), -np.sin(pitch_rad)],
        [0, np.sin(pitch_rad), np.cos(pitch_rad)]
    ])
    
    # Roll (Z-axis)
    R_roll = np.array([
        [np.cos(roll_rad), -np.sin(roll_rad), 0],
        [np.sin(roll_rad), np.cos(roll_rad), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation
    R = R_roll @ R_pitch @ R_yaw
    
    # Generate perspective grid
    f = 0.5 * width_out / np.tan(0.5 * fov_rad)  # Focal length
    
    # Create mesh grid for output image
    x = np.arange(width_out)
    y = np.arange(height_out)
    x, y = np.meshgrid(x, y)
    
    # Convert to normalized coordinates
    x_norm = (x - width_out / 2) / f
    y_norm = (y - height_out / 2) / f
    z_norm = np.ones_like(x_norm)
    
    # Stack into 3D vectors
    xyz = np.stack([x_norm, y_norm, z_norm], axis=-1)
    
    # Normalize
    xyz_norm = xyz / np.linalg.norm(xyz, axis=-1, keepdims=True)
    
    # Apply rotation
    xyz_rot = np.einsum('ij,mnj->mni', R, xyz_norm)
    
    # Convert to spherical coordinates
    lon = np.arctan2(xyz_rot[..., 0], xyz_rot[..., 2])
    lat = np.arcsin(np.clip(xyz_rot[..., 1], -1.0, 1.0))
    
    # Convert to equirectangular pixel coordinates
    u = ((lon / np.pi + 1) / 2 * width_eq).astype(np.float32)
    v = ((lat / np.pi * 2 + 1) / 2 * height_eq).astype(np.float32)
    
    # Remap using cv2 (very fast!)
    perspective_frame = cv2.remap(
        equirect_frame,
        u, v,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_WRAP
    )
    
    return perspective_frame


def extract_perspective_frames_from_360(
    video_path: str,
    output_dir: Path,
    num_views: int = 12,
    fov: float = 90.0,
    output_resolution: Tuple[int, int] = (1920, 1080),
    target_fps: float = 5.0,
    max_frames: int = 300,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Extract perspective frames from 360° video
    
    Args:
        video_path: Path to 360° video
        output_dir: Directory to save perspective frames
        num_views: Number of different perspective views per frame
        fov: Field of view in degrees
        output_resolution: (width, height) of output frames
        target_fps: Target frame extraction rate
        max_frames: Maximum number of frames to extract
        progress_callback: Optional callback(current, total)
    
    Returns:
        Dictionary with extraction statistics
    """
    try:
        logger.info(f"🌐 Extracting perspective frames from 360° video")
        logger.info(f"   Views: {num_views}, FOV: {fov}°, Resolution: {output_resolution}")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        native_fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / native_fps if native_fps > 0 else 0
        
        logger.info(f"📹 Video: {total_frames} frames @ {native_fps:.1f} fps ({duration:.1f}s)")
        
        # Calculate frame sampling
        frame_interval = max(1, int(native_fps / target_fps))
        num_source_frames = min(total_frames // frame_interval, max_frames // num_views)
        
        # Generate camera positions
        positions = generate_optimal_camera_positions(num_views, fov, include_vertical=True)
        
        logger.info(f"⚙️  Extracting {num_source_frames} source frames x {len(positions)} views = {num_source_frames * len(positions)} total frames")
        
        extracted_count = 0
        frame_idx = 0
        source_frame_count = 0
        
        while source_frame_count < num_source_frames:
            # Seek to next frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # For each camera position, extract perspective view
            for view_idx, (yaw, pitch, roll) in enumerate(positions):
                # Convert to perspective
                persp_frame = equirect_to_perspective_fast(
                    frame, yaw, pitch, roll, fov, output_resolution
                )
                
                # Save frame
                frame_filename = f"frame_{source_frame_count:06d}_view_{view_idx:02d}.jpg"
                frame_path = output_dir / frame_filename
                
                cv2.imwrite(str(frame_path), persp_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                extracted_count += 1
            
            source_frame_count += 1
            frame_idx += frame_interval
            
            # Progress callback
            if progress_callback:
                total_expected = num_source_frames * len(positions)
                progress_callback(extracted_count, total_expected)
            
            if extracted_count % (len(positions) * 10) == 0:
                logger.info(f"   Extracted {extracted_count} frames...")
        
        cap.release()
        
        logger.info(f"✅ Extracted {extracted_count} perspective frames from 360° video")
        
        return {
            "status": "success",
            "total_frames": extracted_count,
            "source_frames": source_frame_count,
            "views_per_frame": len(positions),
            "output_directory": str(output_dir),
            "resolution": output_resolution,
            "fov": fov
        }
        
    except Exception as e:
        logger.error(f"❌ 360° frame extraction failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "total_frames": 0
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python video_360_optimizer.py <360_video.mp4> <output_dir> [num_views] [fov]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = Path(sys.argv[2])
    num_views = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    fov = float(sys.argv[4]) if len(sys.argv) > 4 else 90.0
    
    logging.basicConfig(level=logging.INFO)
    
    result = extract_perspective_frames_from_360(
        video_path=video_path,
        output_dir=output_dir,
        num_views=num_views,
        fov=fov
    )
    
    print(f"\n{'='*60}")
    print("360° Frame Extraction Result:")
    print(f"{'='*60}")
    for key, value in result.items():
        print(f"{key}: {value}")

