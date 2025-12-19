#!/usr/bin/env python3
"""
Unified Video Processing Module for Metroa Labs
Consolidates: video_analyzer.py, video_360_optimizer.py, video_360_converter.py
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Video Analysis
# ============================================================================

def analyze_video(video_path: str) -> Dict[str, Any]:
    """
    Analyze video file and extract metadata
    
    Returns:
        Dict with keys: duration, width, height, fps, codec, bitrate, frame_count
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Extract video stream
        video_stream = next(
            (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        format_data = data.get('format', {})
        
        # Calculate FPS
        fps_str = video_stream.get('r_frame_rate', '30/1')
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 30.0
        
        # Calculate duration
        duration = float(format_data.get('duration', 0))
        
        # Calculate frame count
        frame_count = int(video_stream.get('nb_frames', 0))
        if frame_count == 0 and duration > 0:
            frame_count = int(duration * fps)
        
        return {
            'duration': duration,
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'fps': round(fps, 2),
            'codec': video_stream.get('codec_name', 'unknown'),
            'bitrate': int(format_data.get('bit_rate', 0)),
            'frame_count': frame_count,
            'pixel_format': video_stream.get('pix_fmt', 'unknown'),
        }
        
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        return {
            'duration': 0,
            'width': 0,
            'height': 0,
            'fps': 30.0,
            'codec': 'unknown',
            'bitrate': 0,
            'frame_count': 0,
        }


# ============================================================================
# 360° Video Detection & Conversion
# ============================================================================

def detect_360_video(video_path: str) -> Dict[str, Any]:
    """
    Detect if video is 360° format
    
    Returns:
        Dict with keys: is_360, format, width, height, projection
    """
    try:
        metadata = analyze_video(video_path)
        width = metadata['width']
        height = metadata['height']
        
        # Common 360° resolutions
        is_360 = False
        format_type = 'standard'
        projection = 'perspective'
        
        # Check aspect ratio (360° videos are typically 2:1)
        aspect_ratio = width / height if height > 0 else 0
        
        if 1.9 < aspect_ratio < 2.1:  # 2:1 ratio
            is_360 = True
            format_type = 'equirectangular'
            projection = 'equirectangular'
        elif width == height:  # 1:1 ratio (some 360° formats)
            is_360 = True
            format_type = 'cube_map'
            projection = 'cubemap'
        
        # Check for common 360° resolutions
        known_360_resolutions = [
            (3840, 1920),  # 4K 360
            (5760, 2880),  # 6K 360
            (7680, 3840),  # 8K 360
            (4096, 2048),  # Cinema 4K 360
        ]
        
        if (width, height) in known_360_resolutions:
            is_360 = True
            format_type = 'equirectangular'
            projection = 'equirectangular'
        
        return {
            'is_360': is_360,
            'format': format_type,
            'width': width,
            'height': height,
            'projection': projection,
            'aspect_ratio': round(aspect_ratio, 2),
        }
        
    except Exception as e:
        logger.error(f"360° detection failed: {e}")
        return {
            'is_360': False,
            'format': 'standard',
            'width': 0,
            'height': 0,
            'projection': 'perspective',
        }


def convert_360_to_perspective_frames(
    video_path: str,
    output_dir: str,
    target_fps: int = 10,
    num_views: int = 6,
    resolution: int = 1920
) -> int:
    """
    Convert 360° equirectangular video to perspective frames
    
    Args:
        video_path: Path to input 360° video
        output_dir: Directory to save extracted frames
        target_fps: Frame extraction rate
        num_views: Number of perspective views per frame (4 or 6)
        resolution: Output resolution per view
    
    Returns:
        Number of frames extracted
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Define perspective views (yaw, pitch in degrees)
        if num_views == 4:
            views = [
                (0, 0),     # Front
                (90, 0),    # Right
                (180, 0),   # Back
                (270, 0),   # Left
            ]
        else:  # 6 views
            views = [
                (0, 0),     # Front
                (90, 0),    # Right
                (180, 0),   # Back
                (270, 0),   # Left
                (0, 45),    # Up-Front
                (0, -45),   # Down-Front
            ]
        
        frame_count = 0
        
        # Extract frames at target FPS
        for view_idx, (yaw, pitch) in enumerate(views):
            logger.info(f"Extracting view {view_idx + 1}/{len(views)}: yaw={yaw}°, pitch={pitch}°")
            
            # Use ffmpeg v360 filter to convert equirectangular to perspective
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"v360=e:flat:yaw={yaw}:pitch={pitch}:w={resolution}:h={resolution},fps={target_fps}",
                '-q:v', '2',  # High quality
                f"{output_dir}/frame_%04d_view{view_idx}.jpg"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Count extracted frames for this view
            view_frames = len(list(output_path.glob(f"frame_*_view{view_idx}.jpg")))
            frame_count += view_frames
        
        logger.info(f"✅ Extracted {frame_count} perspective frames from 360° video")
        return frame_count
        
    except Exception as e:
        logger.error(f"360° conversion failed: {e}")
        return 0


# ============================================================================
# Video Optimization
# ============================================================================

def optimize_video(
    input_path: str,
    output_path: str,
    target_resolution: Optional[int] = None,
    target_bitrate: Optional[str] = None,
    target_fps: Optional[int] = None
) -> bool:
    """
    Optimize video file (compress, resize, change FPS)
    
    Args:
        input_path: Input video file
        output_path: Output video file
        target_resolution: Max dimension (e.g., 1920 for 1080p)
        target_bitrate: Target bitrate (e.g., '5M')
        target_fps: Target frame rate
    
    Returns:
        True if successful
    """
    try:
        cmd = ['ffmpeg', '-i', input_path]
        
        # Build filter complex
        filters = []
        
        if target_resolution:
            filters.append(f"scale='min({target_resolution},iw)':'min({target_resolution},ih)':force_original_aspect_ratio=decrease")
        
        if target_fps:
            filters.append(f"fps={target_fps}")
        
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        if target_bitrate:
            cmd.extend(['-b:v', target_bitrate])
        
        # Output settings
        cmd.extend([
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'medium',  # Encoding speed
            '-crf', '23',  # Quality (lower = better)
            '-y',  # Overwrite output
            output_path
        ])
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"✅ Video optimized: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Video optimization failed: {e}")
        return False


if __name__ == "__main__":
    # CLI interface
    if len(sys.argv) < 2:
        print("Usage: python video_processing.py <command> <args>")
        print("Commands:")
        print("  analyze <video>")
        print("  detect360 <video>")
        print("  convert360 <video> <output_dir>")
        print("  optimize <input> <output>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        result = analyze_video(sys.argv[2])
        print(json.dumps(result, indent=2))
    elif command == "detect360":
        result = detect_360_video(sys.argv[2])
        print(json.dumps(result, indent=2))
    elif command == "convert360":
        frame_count = convert_360_to_perspective_frames(sys.argv[2], sys.argv[3])
        print(f"Extracted {frame_count} frames")
    elif command == "optimize":
        success = optimize_video(sys.argv[2], sys.argv[3])
        print("Success" if success else "Failed")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

