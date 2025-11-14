#!/usr/bin/env python3
"""
360° Video Converter
Detects and converts equirectangular/spherical 360° videos to perspective images for COLMAP
"""

import cv2
import numpy as np
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)


def detect_360_video(video_path: str) -> Dict[str, any]:
    """
    Detect if video is 360° format (equirectangular/spherical)
    
    Returns:
        {
            'is_360': bool,
            'format': str ('equirectangular'|'spherical'|'unknown'),
            'width': int,
            'height': int,
            'aspect_ratio': float
        }
    """
    try:
        # Use ffprobe to get video metadata
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,display_aspect_ratio",
            "-of", "json",
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        
        if not data.get('streams'):
            return {'is_360': False, 'format': 'unknown'}
        
        stream = data['streams'][0]
        width = int(stream.get('width', 0))
        height = int(stream.get('height', 0))
        aspect_ratio = width / height if height > 0 else 0
        
        # Heuristics for 360° detection:
        # 1. Aspect ratio ~2:1 (equirectangular)
        # 2. Width is typically 2x height
        # 3. Common resolutions: 3840x1920, 5760x2880, 7680x3840
        
        is_360 = False
        format_type = 'unknown'
        
        if 1.8 <= aspect_ratio <= 2.2:  # Close to 2:1
            is_360 = True
            format_type = 'equirectangular'
        elif width >= 3840 and height >= 1920:  # High resolution, likely 360°
            is_360 = True
            format_type = 'equirectangular'
        
        return {
            'is_360': is_360,
            'format': format_type,
            'width': width,
            'height': height,
            'aspect_ratio': aspect_ratio
        }
    except Exception as e:
        logger.warning(f"Could not detect 360° format: {e}")
        return {'is_360': False, 'format': 'unknown'}


def equirectangular_to_perspective(
    equirect_img: np.ndarray,
    fov: float = 90.0,
    yaw: float = 0.0,
    pitch: float = 0.0,
    roll: float = 0.0,
    output_width: int = 1920,
    output_height: int = 1080
) -> np.ndarray:
    """
    Convert equirectangular 360° image to perspective projection
    
    Args:
        equirect_img: Input equirectangular image (H x W x 3)
        fov: Field of view in degrees (default: 90°)
        yaw: Horizontal rotation in degrees (0-360)
        pitch: Vertical rotation in degrees (-90 to 90)
        roll: Roll rotation in degrees
        output_width: Output image width
        output_height: Output image height
    
    Returns:
        Perspective image
    """
    h, w = equirect_img.shape[:2]
    
    # Convert angles to radians
    fov_rad = np.deg2rad(fov)
    yaw_rad = np.deg2rad(yaw)
    pitch_rad = np.deg2rad(pitch)
    roll_rad = np.deg2rad(roll)
    
    # Calculate focal length from FOV
    focal_length = output_width / (2 * np.tan(fov_rad / 2))
    
    # Create output image
    output = np.zeros((output_height, output_width, 3), dtype=np.uint8)
    
    # Generate pixel coordinates in output image
    x = np.arange(output_width)
    y = np.arange(output_height)
    X, Y = np.meshgrid(x, y)
    
    # Normalize coordinates to [-1, 1]
    x_norm = (X - output_width / 2) / focal_length
    y_norm = (Y - output_height / 2) / focal_length
    
    # Create direction vectors
    z = np.ones_like(x_norm)
    directions = np.stack([x_norm, y_norm, z], axis=-1)
    directions = directions / np.linalg.norm(directions, axis=-1, keepdims=True)
    
    # Apply rotations (yaw, pitch, roll)
    # Rotation matrices
    cos_yaw, sin_yaw = np.cos(yaw_rad), np.sin(yaw_rad)
    cos_pitch, sin_pitch = np.cos(pitch_rad), np.sin(pitch_rad)
    cos_roll, sin_roll = np.cos(roll_rad), np.sin(roll_rad)
    
    # Yaw rotation (around Y axis)
    R_yaw = np.array([
        [cos_yaw, 0, sin_yaw],
        [0, 1, 0],
        [-sin_yaw, 0, cos_yaw]
    ])
    
    # Pitch rotation (around X axis)
    R_pitch = np.array([
        [1, 0, 0],
        [0, cos_pitch, -sin_pitch],
        [0, sin_pitch, cos_pitch]
    ])
    
    # Roll rotation (around Z axis)
    R_roll = np.array([
        [cos_roll, -sin_roll, 0],
        [sin_roll, cos_roll, 0],
        [0, 0, 1]
    ])
    
    # Combined rotation
    R = R_roll @ R_pitch @ R_yaw
    
    # Apply rotation to directions
    directions_rotated = directions @ R.T
    
    # Convert 3D directions to equirectangular coordinates
    x_3d, y_3d, z_3d = directions_rotated[..., 0], directions_rotated[..., 1], directions_rotated[..., 2]
    
    # Convert to spherical coordinates
    theta = np.arctan2(x_3d, z_3d)  # Azimuth (longitude)
    phi = np.arccos(y_3d)  # Elevation (latitude)
    
    # Convert to pixel coordinates in equirectangular image
    u = ((theta / np.pi) + 1) * (w / 2)
    v = (phi / np.pi) * h
    
    # Sample from equirectangular image using bilinear interpolation
    u = np.clip(u, 0, w - 1)
    v = np.clip(v, 0, h - 1)
    
    u0 = np.floor(u).astype(int)
    u1 = np.minimum(u0 + 1, w - 1)
    v0 = np.floor(v).astype(int)
    v1 = np.minimum(v0 + 1, h - 1)
    
    # Bilinear interpolation weights
    wu = u - u0
    wv = v - v0
    
    # Sample pixels
    for c in range(3):
        output[:, :, c] = (
            (1 - wu) * (1 - wv) * equirect_img[v0, u0, c] +
            wu * (1 - wv) * equirect_img[v0, u1, c] +
            (1 - wu) * wv * equirect_img[v1, u0, c] +
            wu * wv * equirect_img[v1, u1, c]
        ).astype(np.uint8)
    
    return output


def convert_360_video_to_perspective_frames(
    video_path: str,
    output_dir: Path,
    fov: float = 90.0,
    num_views: int = 8,
    progress_callback=None
) -> int:
    """
    Extract perspective frames from 360° video
    
    Args:
        video_path: Path to 360° video
        output_dir: Directory to save perspective frames
        fov: Field of view for perspective projection
        num_views: Number of perspective views to extract per frame (evenly spaced yaw angles)
        progress_callback: Optional callback(progress, total)
    
    Returns:
        Number of frames extracted
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frame_count = 0
    frame_idx = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Generate multiple perspective views from this 360° frame
            yaw_step = 360.0 / num_views
            
            for view_idx in range(num_views):
                yaw = view_idx * yaw_step
                perspective_frame = equirectangular_to_perspective(
                    frame,
                    fov=fov,
                    yaw=yaw,
                    pitch=0.0,
                    roll=0.0
                )
                
                # Save perspective frame
                output_filename = output_dir / f"frame_{frame_idx:06d}_view_{view_idx:02d}.jpg"
                cv2.imwrite(str(output_filename), perspective_frame)
            
            frame_idx += 1
            frame_count += num_views
            
            if progress_callback:
                progress_callback(frame_idx, total_frames)
        
        logger.info(f"Extracted {frame_count} perspective frames from {frame_idx} 360° frames")
        return frame_count
    
    finally:
        cap.release()

