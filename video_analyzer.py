#!/usr/bin/env python3
"""
Video Analyzer - Intelligent video analysis for optimal reconstruction settings
Automatically detects video type, quality, and characteristics to optimize pipeline
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import re

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Analyze videos to determine optimal reconstruction settings"""
    
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        self.metadata = {}
        self.analysis = {}
        
    def analyze(self) -> Dict[str, Any]:
        """
        Comprehensive video analysis
        
        Returns:
            Dictionary with video characteristics and recommended settings
        """
        try:
            logger.info(f"🔍 Analyzing video: {self.video_path.name}")
            
            # Get metadata using ffprobe
            self._extract_metadata()
            
            # Analyze video characteristics
            self._analyze_characteristics()
            
            # Determine optimal settings
            recommended_settings = self._recommend_settings()
            
            return {
                "metadata": self.metadata,
                "analysis": self.analysis,
                "recommendations": recommended_settings
            }
            
        except Exception as e:
            logger.error(f"❌ Video analysis failed: {e}")
            return self._get_default_analysis()
    
    def _extract_metadata(self):
        """Extract video metadata using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,bit_rate,codec_name,pix_fmt,duration",
                "-show_entries", "format=duration,size,bit_rate",
                "-of", "json",
                str(self.video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract stream info
            if data.get('streams'):
                stream = data['streams'][0]
                
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))
                
                # Parse frame rate
                fps_str = stream.get('r_frame_rate', '30/1')
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    fps = float(num) / float(den)
                else:
                    fps = float(fps_str)
                
                # Get duration (prefer stream duration, fall back to format duration)
                duration = float(stream.get('duration', 0))
                if duration == 0 and data.get('format'):
                    duration = float(data['format'].get('duration', 0))
                
                # Get bitrate
                bit_rate = int(stream.get('bit_rate', 0))
                if bit_rate == 0 and data.get('format'):
                    bit_rate = int(data['format'].get('bit_rate', 0))
                
                # Get codec and pixel format
                codec = stream.get('codec_name', 'unknown')
                pix_fmt = stream.get('pix_fmt', 'unknown')
                
                self.metadata = {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'duration': duration,
                    'bit_rate': bit_rate,
                    'codec': codec,
                    'pix_fmt': pix_fmt,
                    'aspect_ratio': width / height if height > 0 else 0,
                    'total_frames': int(fps * duration) if duration > 0 else 0
                }
                
                logger.info(f"📊 Video: {width}x{height} @ {fps:.1f} fps, {duration:.1f}s, {codec}")
            
        except Exception as e:
            logger.warning(f"Could not extract metadata: {e}")
            self.metadata = self._get_default_metadata()
    
    def _analyze_characteristics(self):
        """Analyze video characteristics to determine type and quality"""
        
        width = self.metadata.get('width', 0)
        height = self.metadata.get('height', 0)
        aspect_ratio = self.metadata.get('aspect_ratio', 0)
        fps = self.metadata.get('fps', 30)
        duration = self.metadata.get('duration', 0)
        bit_rate = self.metadata.get('bit_rate', 0)
        codec = self.metadata.get('codec', 'unknown')
        
        # Detect video type
        video_type = "standard"
        is_360 = False
        
        # Check for 360° video (equirectangular: ~2:1 aspect ratio)
        if 1.8 <= aspect_ratio <= 2.2:
            video_type = "360_equirectangular"
            is_360 = True
            logger.info("🌐 Detected 360° equirectangular video")
        elif width >= 3840 and height >= 1920 and aspect_ratio >= 1.8:
            video_type = "360_equirectangular"
            is_360 = True
            logger.info("🌐 Detected 4K+ 360° video")
        
        # Detect professional vs consumer camera
        is_professional = False
        if width >= 3840 or (bit_rate > 50000000 and width >= 1920):  # 4K or high bitrate 1080p
            is_professional = True
            camera_type = "professional"
            logger.info("📹 Detected professional/4K camera")
        elif width >= 1920:
            camera_type = "consumer_hd"
            logger.info("📱 Detected consumer HD camera")
        else:
            camera_type = "consumer_sd"
            logger.info("📱 Detected consumer SD camera")
        
        # Motion analysis (based on FPS and duration)
        if fps >= 60:
            motion_type = "high_speed"
        elif fps >= 30:
            motion_type = "normal"
        else:
            motion_type = "low_fps"
        
        # Video length category
        if duration < 15:
            length_category = "short"
        elif duration < 45:
            length_category = "medium"
        elif duration < 120:
            length_category = "long"
        else:
            length_category = "very_long"
        
        # Compression quality
        if bit_rate > 0:
            # Calculate bits per pixel per frame
            pixels = width * height
            if pixels > 0 and fps > 0:
                bpp = bit_rate / (pixels * fps)
                if bpp > 0.5:
                    compression_quality = "high"
                elif bpp > 0.2:
                    compression_quality = "medium"
                else:
                    compression_quality = "low"
            else:
                compression_quality = "unknown"
        else:
            compression_quality = "unknown"
        
        self.analysis = {
            'video_type': video_type,
            'is_360': is_360,
            'is_professional': is_professional,
            'camera_type': camera_type,
            'motion_type': motion_type,
            'length_category': length_category,
            'compression_quality': compression_quality,
            'resolution_category': self._categorize_resolution(width, height)
        }
        
        logger.info(f"🎬 Video type: {camera_type}, {video_type}, {length_category} ({duration:.1f}s)")
    
    def _categorize_resolution(self, width: int, height: int) -> str:
        """Categorize resolution"""
        pixels = width * height
        
        if pixels >= 3840 * 2160:  # 4K
            return "4k"
        elif pixels >= 2560 * 1440:  # 2K
            return "2k"
        elif pixels >= 1920 * 1080:  # 1080p
            return "1080p"
        elif pixels >= 1280 * 720:  # 720p
            return "720p"
        else:
            return "sd"
    
    def _recommend_settings(self) -> Dict[str, Any]:
        """Recommend optimal reconstruction settings based on analysis"""
        
        duration = self.metadata.get('duration', 30)
        is_360 = self.analysis.get('is_360', False)
        is_professional = self.analysis.get('is_professional', False)
        camera_type = self.analysis.get('camera_type', 'consumer_hd')
        length_category = self.analysis.get('length_category', 'medium')
        resolution_category = self.analysis.get('resolution_category', '1080p')
        
        # Recommend quality mode
        quality_mode = "fast"
        
        # Professional camera or 4K: use high_quality
        if is_professional or resolution_category in ['4k', '2k']:
            quality_mode = "high_quality"
        
        # 360° videos: special handling
        if is_360:
            if is_professional:
                quality_mode = "ultra_openmvs"
            else:
                quality_mode = "high_quality"
        
        # Very long videos: use fast mode to save time
        if length_category == "very_long":
            quality_mode = "fast"
        
        # Recommend FPS extraction rate
        if is_360:
            # 360° needs more frames for good coverage
            if duration < 30:
                target_fps = 6
                target_frames = int(duration * target_fps)
            else:
                target_fps = 5
                target_frames = min(int(duration * target_fps), 300)  # Cap at 300 frames
        else:
            # Standard video
            if length_category == "short":
                target_fps = 5
                target_frames = int(duration * target_fps)
            elif length_category == "medium":
                target_fps = 4
                target_frames = int(duration * target_fps)
            else:  # long or very_long
                target_fps = 3
                target_frames = min(int(duration * target_fps), 250)  # Cap at 250 frames
        
        # Recommend max resolution
        if resolution_category in ['4k', '2k']:
            max_resolution = 2560  # Downscale 4K to 2.5K
        elif resolution_category == '1080p':
            max_resolution = 1920  # Keep 1080p
        else:
            max_resolution = 1280  # Upscale SD to 720p
        
        # Recommend 360° conversion settings
        conversion_settings = None
        if is_360:
            # For 360° videos, extract perspective views
            conversion_settings = {
                'num_views': 12 if is_professional else 8,  # Number of perspective views to extract
                'fov': 90,  # Field of view
                'overlap': 30,  # Overlap between views in degrees
                'output_resolution': (1920, 1080)  # Perspective frame resolution
            }
        
        recommendations = {
            'quality_mode': quality_mode,
            'target_fps': target_fps,
            'target_frames': target_frames,
            'max_resolution': max_resolution,
            'enable_mesh_generation': True,  # Always generate mesh
            'mesh_quality': "medium" if quality_mode == "fast" else "high",
            'is_360': is_360,
            'conversion_settings': conversion_settings,
            'estimated_time': self._estimate_processing_time(
                quality_mode, target_frames, resolution_category, is_360
            )
        }
        
        logger.info(f"💡 Recommended: {quality_mode} mode, {target_frames} frames @ {max_resolution}p")
        logger.info(f"   Estimated time: {recommendations['estimated_time']}")
        
        return recommendations
    
    def _estimate_processing_time(
        self,
        quality_mode: str,
        num_frames: int,
        resolution: str,
        is_360: bool
    ) -> str:
        """Estimate processing time"""
        
        # Base time per frame (seconds)
        base_times = {
            "fast": 1.0,
            "high_quality": 2.5,
            "ultra_openmvs": 5.0
        }
        
        base_time = base_times.get(quality_mode, 1.5)
        
        # Resolution multiplier
        res_multipliers = {
            "4k": 1.5,
            "2k": 1.2,
            "1080p": 1.0,
            "720p": 0.8,
            "sd": 0.6
        }
        
        res_mult = res_multipliers.get(resolution, 1.0)
        
        # 360° video adds overhead
        if is_360:
            res_mult *= 1.3
        
        total_seconds = int(base_time * num_frames * res_mult)
        
        # Add mesh generation time
        if quality_mode == "fast":
            total_seconds += 20
        elif quality_mode == "high_quality":
            total_seconds += 40
        else:
            total_seconds += 60
        
        # Format as human-readable
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 180:
            return f"{total_seconds // 60}m {total_seconds % 60}s"
        else:
            return f"{total_seconds // 60}m"
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """Return default metadata if extraction fails"""
        return {
            'width': 1920,
            'height': 1080,
            'fps': 30.0,
            'duration': 30.0,
            'bit_rate': 10000000,
            'codec': 'unknown',
            'pix_fmt': 'yuv420p',
            'aspect_ratio': 1.78,
            'total_frames': 900
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis if detection fails"""
        return {
            "metadata": self._get_default_metadata(),
            "analysis": {
                'video_type': 'standard',
                'is_360': False,
                'is_professional': False,
                'camera_type': 'consumer_hd',
                'motion_type': 'normal',
                'length_category': 'medium',
                'compression_quality': 'unknown',
                'resolution_category': '1080p'
            },
            "recommendations": {
                'quality_mode': 'fast',
                'target_fps': 4,
                'target_frames': 120,
                'max_resolution': 1920,
                'enable_mesh_generation': True,
                'mesh_quality': 'medium',
                'is_360': False,
                'conversion_settings': None,
                'estimated_time': '2m'
            }
        }


def analyze_video(video_path: str) -> Dict[str, Any]:
    """
    Convenience function to analyze a video
    
    Args:
        video_path: Path to video file
    
    Returns:
        Analysis results with recommendations
    """
    analyzer = VideoAnalyzer(video_path)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_analyzer.py <video_file>")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    
    result = analyze_video(sys.argv[1])
    
    print("\n" + "="*60)
    print("VIDEO ANALYSIS RESULT")
    print("="*60)
    
    print("\n📹 METADATA:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\n🎬 ANALYSIS:")
    for key, value in result['analysis'].items():
        print(f"  {key}: {value}")
    
    print("\n💡 RECOMMENDATIONS:")
    for key, value in result['recommendations'].items():
        if value is not None:
            print(f"  {key}: {value}")
    
    print("\n" + "="*60)

