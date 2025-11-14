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
    Convert equirectangular 360° image to perspective projection using cv2.remap() for optimal performance
    
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
    
    # Generate pixel coordinates in output image
    x = np.arange(output_width, dtype=np.float32)
    y = np.arange(output_height, dtype=np.float32)
    X, Y = np.meshgrid(x, y)
    
    # Normalize coordinates to [-1, 1] range
    x_norm = (X - output_width / 2) / focal_length
    y_norm = (Y - output_height / 2) / focal_length
    
    # Create direction vectors (normalized)
    z = np.ones_like(x_norm)
    norm = np.sqrt(x_norm**2 + y_norm**2 + z**2)
    x_3d = x_norm / norm
    y_3d = y_norm / norm
    z_3d = z / norm
    
    # Apply rotations (yaw, pitch, roll) using rotation matrices
    cos_yaw, sin_yaw = np.cos(yaw_rad), np.sin(yaw_rad)
    cos_pitch, sin_pitch = np.cos(pitch_rad), np.sin(pitch_rad)
    cos_roll, sin_roll = np.cos(roll_rad), np.sin(roll_rad)
    
    # Yaw rotation (around Y axis)
    x_rot = x_3d * cos_yaw + z_3d * sin_yaw
    z_rot = -x_3d * sin_yaw + z_3d * cos_yaw
    x_3d, z_3d = x_rot, z_rot
    
    # Pitch rotation (around X axis)
    y_rot = y_3d * cos_pitch - z_3d * sin_pitch
    z_rot = y_3d * sin_pitch + z_3d * cos_pitch
    y_3d, z_3d = y_rot, z_rot
    
    # Roll rotation (around Z axis)
    x_rot = x_3d * cos_roll - y_3d * sin_roll
    y_rot = x_3d * sin_roll + y_3d * cos_roll
    x_3d, y_3d = x_rot, y_rot
    
    # Convert 3D directions to spherical coordinates
    theta = np.arctan2(x_3d, z_3d)  # Azimuth (longitude) [-π, π]
    phi = np.arccos(np.clip(y_3d, -1.0, 1.0))  # Elevation (latitude) [0, π]
    
    # Convert spherical coordinates to equirectangular pixel coordinates
    # Longitude: theta [-π, π] -> u [0, w]
    u = ((theta / np.pi) + 1.0) * (w / 2.0)
    # Latitude: phi [0, π] -> v [0, h]
    v = (phi / np.pi) * h
    
    # Ensure coordinates are within valid range for remap
    # cv2.remap handles out-of-bounds with border interpolation
    map_x = u.astype(np.float32)
    map_y = v.astype(np.float32)
    
    # Use cv2.remap for fast, optimized bilinear interpolation
    # INTER_LINEAR: bilinear interpolation (default, fastest)
    # BORDER_WRAP: wrap around for 360° images (handles edge cases)
    output = cv2.remap(
        equirect_img,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_WRAP  # Wrap around for seamless 360° images
    )
    
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

