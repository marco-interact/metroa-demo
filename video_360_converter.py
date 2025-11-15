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
    extraction_fps: float = 1.0,
    progress_callback=None
) -> int:
    """
    Extract perspective frames from 360° video
    
    OPTIMIZED: Extracts only 1 frame per second, then generates multiple perspective views
    from each frame. This is much more efficient than processing every frame.
    
    Args:
        video_path: Path to 360° video
        output_dir: Directory to save perspective frames
        fov: Field of view for perspective projection
        num_views: Number of perspective views to extract per frame (evenly spaced yaw angles)
        extraction_fps: FPS for frame extraction (default: 1.0 = 1 frame per second)
        progress_callback: Optional callback(progress, total)
    
    Returns:
        Number of perspective frames generated (extraction_fps * video_duration * num_views)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get video duration using ffprobe
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        probe_result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True)
        video_duration = float(probe_result.stdout.strip())
        estimated_frames = int(video_duration * extraction_fps)
        logger.info(f"📹 Video duration: {video_duration:.1f}s → extracting {estimated_frames} frames at {extraction_fps} fps")
    except Exception as e:
        logger.warning(f"Could not detect video duration: {e}, using default")
        video_duration = 60.0
        estimated_frames = int(video_duration * extraction_fps)
    
    # Step 1: Extract frames at 1 fps using FFmpeg (much faster than OpenCV)
    temp_frames_dir = output_dir / "temp_equirectangular"
    temp_frames_dir.mkdir(parents=True, exist_ok=True)
    
    temp_frame_pattern = temp_frames_dir / "frame_%06d.jpg"
    
    logger.info(f"🌐 Step 1: Extracting {extraction_fps} fps from 360° video...")
    extract_cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"fps={extraction_fps}",
        "-q:v", "2",  # High quality JPEG
        "-y",  # Overwrite
        str(temp_frame_pattern)
    ]
    
    try:
        subprocess.run(extract_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Frame extraction failed: {e.stderr}")
        raise RuntimeError(f"Failed to extract frames: {e.stderr}")
    
    # Count extracted frames
    extracted_frames = sorted(temp_frames_dir.glob("frame_*.jpg"))
    logger.info(f"✅ Extracted {len(extracted_frames)} equirectangular frames")
    
    # Step 2: Generate perspective views from each extracted frame
    logger.info(f"🌐 Step 2: Generating {num_views} perspective views per frame...")
    frame_count = 0
    yaw_step = 360.0 / num_views
    
    for frame_idx, equirect_frame_path in enumerate(extracted_frames):
        # Load equirectangular frame
        equirect_frame = cv2.imread(str(equirect_frame_path))
        if equirect_frame is None:
            logger.warning(f"Could not load frame: {equirect_frame_path}")
            continue
        
        # Generate multiple perspective views from this frame
        for view_idx in range(num_views):
            yaw = view_idx * yaw_step
            perspective_frame = equirectangular_to_perspective(
                equirect_frame,
                fov=fov,
                yaw=yaw,
                pitch=0.0,
                roll=0.0
            )
            
            # Save perspective frame
            output_filename = output_dir / f"frame_{frame_idx:06d}_view_{view_idx:02d}.jpg"
            cv2.imwrite(str(output_filename), perspective_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            frame_count += 1
        
        # Update progress
        if progress_callback:
            progress_callback(frame_idx + 1, len(extracted_frames))
    
    # Cleanup temporary equirectangular frames
    try:
        import shutil
        shutil.rmtree(temp_frames_dir)
        logger.info(f"🧹 Cleaned up temporary frames")
    except Exception as e:
        logger.warning(f"Could not cleanup temp frames: {e}")
    
    logger.info(f"✅ Generated {frame_count} perspective frames from {len(extracted_frames)} equirectangular frames ({num_views} views each)")
    return frame_count


def extract_360_frame(
    video_path: str,
    output_path: Path,
    time_seconds: float = 0.0,
    keep_equirectangular: bool = True,
    perspective_fov: float = 90.0,
    perspective_yaw: float = 0.0,
    perspective_pitch: float = 0.0
) -> Path:
    """
    Extract a single frame from 360° video using FFmpeg v360 filter
    
    This is more efficient than loading entire video into OpenCV for single frame extraction.
    Uses FFmpeg's hardware-accelerated v360 filter when available.
    
    Args:
        video_path: Input 360° video file path
        output_path: Output image path (will be created)
        time_seconds: Time position in video (default: 0.0 = first frame)
        keep_equirectangular: If True, keep equirectangular format (no conversion).
                             If False, convert to perspective projection.
        perspective_fov: Field of view in degrees (if converting to perspective)
        perspective_yaw: Yaw angle in degrees (if converting to perspective)
        perspective_pitch: Pitch angle in degrees (if converting to perspective)
    
    Returns:
        Path to extracted frame
    
    Example:
        # Extract equirectangular frame at 5 seconds
        frame = extract_360_frame(
            "video.mp4", 
            Path("frame.jpg"), 
            time_seconds=5.0,
            keep_equirectangular=True
        )
        
        # Extract perspective frame (converted)
        frame = extract_360_frame(
            "video.mp4",
            Path("frame_perspective.jpg"),
            time_seconds=5.0,
            keep_equirectangular=False,
            perspective_yaw=45.0  # Look 45° to the right
        )
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if keep_equirectangular:
        # Use v360 filter to keep equirectangular format (no conversion)
        # input=e:output=e means equirectangular to equirectangular
        cmd = [
            "ffmpeg",
            "-ss", str(time_seconds),  # Seek to time position
            "-i", str(video_path),
            "-vf", "v360=input=e:output=e",  # Keep equirectangular format
            "-frames:v", "1",  # Extract only 1 frame
            "-y",  # Overwrite output file
            str(output_path)
        ]
    else:
        # Convert to perspective projection
        # v360 filter: equirectangular input → perspective output
        cmd = [
            "ffmpeg",
            "-ss", str(time_seconds),
            "-i", str(video_path),
            "-vf", f"v360=input=e:output=perspective:pitch={perspective_pitch}:yaw={perspective_yaw}:fov={perspective_fov}",
            "-frames:v", "1",
            "-y",
            str(output_path)
        ]
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        logger.info(f"✅ Extracted 360° frame at {time_seconds}s to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg frame extraction failed: {e.stderr}")
        raise RuntimeError(f"Failed to extract frame: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Frame extraction timed out after 30s")
        raise RuntimeError("Frame extraction timed out")

