#!/usr/bin/env python3
"""
COLMAP Processing Pipeline
Implements video -> 3D point cloud reconstruction
Based on: https://colmap.github.io/tutorial.html
"""

import subprocess
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import shutil

logger = logging.getLogger(__name__)

# Import 360° video converter if available
try:
    from video_360_converter import detect_360_video, convert_360_video_to_perspective_frames
    HAS_360_SUPPORT = True
except ImportError:
    HAS_360_SUPPORT = False
    logger.warning("360° video support not available (video_360_converter.py not found)")


class COLMAPProcessor:
    """COLMAP 3D Reconstruction Processor"""
    
    def __init__(self, job_path: str):
        """
        Initialize COLMAP processor with standard workspace structure
        Reference: https://colmap.github.io/tutorial.html#data-structure
        """
        self.job_path = Path(job_path)
        
        # Standard COLMAP workspace structure
        # Reference: https://colmap.github.io/tutorial.html#data-structure
        self.images_path = self.job_path / "images"        # Extracted frames
        self.database_path = self.job_path / "database.db" # SQLite database
        self.sparse_path = self.job_path / "sparse"        # Sparse models (0/, 1/, etc.)
        self.dense_path = self.job_path / "dense"          # Dense reconstruction
        
        # Create directories
        self._create_directories()
        
        # Setup environment for headless COLMAP execution
        self.env = os.environ.copy()
        self.env['DISPLAY'] = os.getenv('DISPLAY', ':99')
        self.env['QT_QPA_PLATFORM'] = 'offscreen'
        self.env['MESA_GL_VERSION_OVERRIDE'] = '3.3'
        
        # Detect GPU availability
        self.gpu_available = self._check_gpu_available()
    
    def _create_directories(self):
        """
        Create COLMAP workspace directory structure
        Following: https://colmap.github.io/tutorial.html#data-structure
        """
        self.images_path.mkdir(parents=True, exist_ok=True)
        self.sparse_path.mkdir(parents=True, exist_ok=True)
        self.dense_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created COLMAP workspace at {self.job_path}")
    
    def _check_gpu_available(self) -> bool:
        """
        Check if GPU is available for COLMAP processing
        Tests both nvidia-smi and CUDA availability
        """
        try:
            # Check if nvidia-smi works
            result = subprocess.run(
                ["nvidia-smi"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ GPU detected via nvidia-smi")
                return True
            else:
                logger.warning("⚠️  nvidia-smi failed, falling back to CPU")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.warning(f"⚠️  GPU check failed: {e}, falling back to CPU")
            return False
    
    def _auto_detect_optimal_fps(self, video_path: str, quality: str = "medium") -> Tuple[float, float, int]:
        """
        Auto-detect optimal FPS based on video duration and quality target
        
        Returns: (optimal_fps, video_duration, total_frames)
        
        Strategy:
        - Short videos (<30s): Use higher FPS (more frames for stability)
        - Medium videos (30s-2min): Use medium FPS (balanced)
        - Long videos (>2min): Use lower FPS (avoid too many frames)
        
        Target frame count for good reconstruction:
        - Low quality: 30-50 frames
        - Medium quality: 50-100 frames  
        - High quality: 100-200 frames
        """
        try:
            # Get video duration and native FPS
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration:stream=r_frame_rate",
                "-of", "default=noprint_wrappers=1",
                str(video_path)
            ]
            
            probe_result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True)
            output_lines = probe_result.stdout.strip().split('\n')
            
            # Parse output
            duration = 0.0
            native_fps = 30.0  # default fallback
            
            for line in output_lines:
                if 'r_frame_rate' in line or '/' in line:
                    fps_str = line.split('=')[-1]
                    if '/' in fps_str:
                        num, den = fps_str.split('/')
                        native_fps = float(num) / float(den)
                elif 'duration' in line:
                    duration = float(line.split('=')[-1])
            
            logger.info(f"📹 Video analysis: duration={duration:.1f}s, native_fps={native_fps:.1f}")
            
            # Define target frame counts based on quality
            # Higher frame counts = better overlap potential
            target_frames = {
                "low": 60,      # Increased for better overlap (was 40)
                "medium": 100,  # Increased for >80% overlap (was 70)
                "high": 150     # Increased for maximum overlap (was 120),
                "ultra": 300,
                "ultra_openmvs": 300
            }
            
            target_frame_count = target_frames.get(quality, 100)
            
            # Calculate optimal FPS to reach target frame count
            # Extract more frames closer together for better physical overlap
            if duration > 0:
                optimal_fps = target_frame_count / duration
                # Increased FPS range for better overlap (was 3-15, now 5-20)
                max_fps = 30 if "ultra" in quality else 20
                optimal_fps = max(5, min(optimal_fps, max_fps))  # Between 5-20 fps for better overlap
                # Don't exceed native FPS
                optimal_fps = min(optimal_fps, native_fps)
            else:
                # Fallback if duration detection fails
                optimal_fps = 10
            
            estimated_frames = int(duration * optimal_fps)
            
            logger.info(f"🎯 Auto-detected optimal FPS: {optimal_fps:.1f} fps → ~{estimated_frames} frames (target: {target_frame_count})")
            
            return optimal_fps, duration, estimated_frames
            
        except Exception as e:
            logger.warning(f"⚠️  Auto-detection failed: {e}, using defaults")
            return 10.0, 20.0, 200  # Safe defaults
    
    def extract_frames(self, video_path: str, max_frames: int = 0, target_fps: int = None, quality: str = "medium", progress_callback=None, is_360: bool = False) -> int:
        """
        Extract frames from video using ffmpeg with AUTO FPS DETECTION
        
        Following COLMAP best practices:
        Reference: https://colmap.github.io/tutorial.html#data-structure
        
        Smart FPS selection:
        - Automatically analyzes video duration
        - Calculates optimal FPS for quality target
        - Balances frame count vs processing speed
        
        Args:
            video_path: Path to input video
            max_frames: Maximum number of frames to extract (0 = auto)
            target_fps: Manual FPS override (None = auto-detect)
            quality: Quality preset (low/medium/high) - affects target frame count
            is_360: If True, treat as 360° video and convert to perspective frames
        """
        # Check for 360° video if not explicitly set
        if not is_360 and HAS_360_SUPPORT:
            try:
                detection = detect_360_video(video_path)
                is_360 = detection.get('is_360', False)
                if is_360:
                    logger.info(f"🌐 Detected 360° video format: {detection.get('format', 'unknown')}")
            except Exception as e:
                logger.warning(f"Could not detect 360° format: {e}")
        
        # Handle 360° video conversion
        if is_360 and HAS_360_SUPPORT:
            logger.info(f"🌐 Converting 360° video to perspective frames (optimized: 1 fps extraction)...")
            try:
                # OPTIMIZED: Extract only 1 frame per second, then generate multiple perspective views
                # This is much more efficient than processing every frame
                num_views = 8  # Extract 8 views per frame (45° apart)
                extraction_fps = 1.0  # Extract 1 frame per second (optimized)
                
                frame_count = convert_360_video_to_perspective_frames(
                    video_path,
                    self.images_path,
                    fov=90.0,
                    num_views=num_views,
                    extraction_fps=extraction_fps,  # 1 fps extraction
                    progress_callback=progress_callback
                )
                logger.info(f"✅ Extracted {frame_count} perspective frames from 360° video (1 fps extraction, {num_views} views per frame)")
                return frame_count
            except Exception as e:
                logger.error(f"360° conversion failed, falling back to standard extraction: {e}")
                # Fall through to standard extraction
        
        logger.info(f"Extracting frames from {video_path} (quality={quality}, auto_fps={'enabled' if target_fps is None else 'manual'})")
        
        # Auto-detect optimal FPS if not specified
        if target_fps is None:
            actual_fps, duration, estimated_frames = self._auto_detect_optimal_fps(video_path, quality)
        else:
            # Manual FPS specified - get video info for logging
            try:
                probe_cmd = [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path)
                ]
                probe_result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True)
                duration = float(probe_result.stdout.strip())
                actual_fps = target_fps
                estimated_frames = int(duration * actual_fps)
                logger.info(f"📹 Manual FPS: {actual_fps} fps → ~{estimated_frames} frames")
            except Exception as e:
                logger.warning(f"Could not detect video duration: {e}")
                actual_fps = target_fps
                duration = 20.0
                estimated_frames = 200
        
        # Quality-based scaling
        scale_map = {
            "low": "1280:-2",
            "medium": "1920:-2", 
            "high": "3840:-2",
            "ultra": "3840:-2",
            "ultra_openmvs": "3840:-2"
        }
        scale = scale_map.get(quality, "1920:-2")
        
        # Extract frames with uniform naming (COLMAP requirement)
        # Format: %06d for frame numbering
        output_pattern = self.images_path / "frame_%06d.jpg"
        
        # Call progress callback at start
        if progress_callback:
            progress_callback(0, estimated_frames)
        
        # Use fps filter to extract at specified FPS
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps={actual_fps},scale={scale}",
            "-q:v", "2",  # High quality JPEG (1-31, lower = better)
            "-y",  # Overwrite existing files
            str(output_pattern)
        ]
        
        # Add frame limit only if specified (max_frames > 0)
        if max_frames > 0:
            cmd.insert(-2, "-frames:v")
            cmd.insert(-2, str(max_frames))
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Count extracted frames
            frame_count = len(list(self.images_path.glob("*.jpg")))
            
            # Call progress callback at completion
            if progress_callback:
                progress_callback(frame_count, frame_count)
            
            logger.info(f"Extracted {frame_count} frames to {self.images_path}")
            return frame_count
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Frame extraction failed: {e.stderr}")
            raise
    
    def extract_features(self, quality: str = "medium", use_gpu: bool = True, progress_callback=None) -> Dict:
        """
        Extract SIFT features from images
        Reference: https://colmap.github.io/tutorial.html#feature-detection-and-extraction
        
        OPTIMIZED FOR RTX 4090: Higher feature counts for denser reconstructions
        RTX 4090 can handle significantly more features than previous generations
        """
        # Override GPU flag if GPU not available
        actual_use_gpu = use_gpu and self.gpu_available
        gpu_mode = "GPU" if actual_use_gpu else "CPU"
        logger.info(f"Extracting features with quality={quality} using {gpu_mode}")
        
        # Quality-based parameters - OPTIMIZED FOR RTX 4090
        # RTX 4090 has massive compute power - use it!
        quality_params = {
            "low": {
                "max_num_features": "16384",    # 2x increase for better reconstruction
                "max_image_size": "2560",       # Higher resolution even for "low"
                "first_octave": "-1",           # Extract at higher resolution
                "num_octaves": "4",             # Standard octave count
                "peak_threshold": "0.0066",     # Lower = more features
            },
            "medium": {
                "max_num_features": "32768",    # 2x increase - RTX 4090 can handle it
                "max_image_size": "3840",       # 4K resolution for better detail
                "first_octave": "-1",           # Extract at higher resolution
                "num_octaves": "4",
                "peak_threshold": "0.0066",
            },
            "high": {
                "max_num_features": "65536",    # 2x increase - maximum detail
                "max_image_size": "4096",       # Full 4K+ resolution
                "first_octave": "-1",           # Extract at higher resolution
                "num_octaves": "4",
                "peak_threshold": "0.0066",
            },
            "ultra": {
                "max_num_features": "131072",   # Extreme feature count
                "max_image_size": "8192",       # 8K resolution support
                "first_octave": "-1",           # Always use original resolution
                "num_octaves": "5",             # More scales
                "peak_threshold": "0.001",      # Extremely sensitive (finds everything)
                "edge_threshold": "15",         # Allow slightly more edge-like features
            }
        }
        
        params = quality_params.get(quality, quality_params["medium"])
        
        # Build command with enhanced COLMAP parameters for maximum quality
        cmd = [
            "colmap", "feature_extractor",
            "--database_path", str(self.database_path),
            "--image_path", str(self.images_path),
            "--ImageReader.single_camera", "1",  # All frames from same camera
            "--ImageReader.camera_model", "OPENCV",  # Use OpenCV camera model
            "--SiftExtraction.max_num_features", params["max_num_features"],
            "--SiftExtraction.max_image_size", params["max_image_size"],
            "--SiftExtraction.first_octave", params["first_octave"],  # Extract at higher resolution
            "--SiftExtraction.num_octaves", params["num_octaves"],
            "--SiftExtraction.octave_resolution", "3",
            "--SiftExtraction.peak_threshold", params["peak_threshold"],  # Lower = more features
            "--SiftExtraction.edge_threshold", "10",
            "--SiftExtraction.use_gpu", "1" if actual_use_gpu else "0",  # GPU control
            "--SiftExtraction.gpu_index", "0",
        ]
        
        try:
            # Get image count for progress tracking
            image_count = len(list(self.images_path.glob("*.jpg")))
            if progress_callback:
                progress_callback(0, image_count)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=self.env)
            
            # Parse statistics
            stats = self._parse_feature_stats(result.stdout)
            
            if progress_callback:
                progress_callback(image_count, image_count)
            
            logger.info(f"Feature extraction complete: {stats}")
            return stats
            
        except subprocess.CalledProcessError as e:
            # Log full error details for debugging
            error_output = e.stderr if e.stderr else e.stdout if e.stdout else "No error output"
            logger.error(f"❌ Feature extraction failed (exit code {e.returncode})")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Error output: {error_output}")
            
            # If GPU was attempted and failed, try CPU fallback
            if actual_use_gpu and ("GPU" in str(error_output) or "CUDA" in str(error_output)):
                logger.warning(f"⚠️  GPU feature extraction failed, retrying with CPU...")
                self.gpu_available = False  # Disable GPU for future calls
                return self.extract_features(quality=quality, use_gpu=False, progress_callback=progress_callback)
            
            # If max_image_size might be the issue, try with a reasonable limit
            if params["max_image_size"] == "0" or int(params.get("max_image_size", 4096)) > 8192:
                logger.warning(f"⚠️  Feature extraction failed with max_image_size={params['max_image_size']}, retrying with 8192...")
                # Create fallback params
                fallback_params = params.copy()
                fallback_params["max_image_size"] = "8192"
                fallback_cmd = [
                    "colmap", "feature_extractor",
                    "--database_path", str(self.database_path),
                    "--image_path", str(self.images_path),
                    "--ImageReader.single_camera", "1",
                    "--ImageReader.camera_model", "OPENCV",
                    "--SiftExtraction.max_num_features", fallback_params["max_num_features"],
                    "--SiftExtraction.max_image_size", fallback_params["max_image_size"],
                    "--SiftExtraction.first_octave", fallback_params["first_octave"],
                    "--SiftExtraction.num_octaves", fallback_params["num_octaves"],
                    "--SiftExtraction.octave_resolution", "3",
                    "--SiftExtraction.peak_threshold", fallback_params["peak_threshold"],
                    "--SiftExtraction.edge_threshold", "10",
                    "--SiftExtraction.use_gpu", "1" if actual_use_gpu else "0",
                    "--SiftExtraction.gpu_index", "0",
                ]
                try:
                    result = subprocess.run(fallback_cmd, check=True, capture_output=True, text=True, env=self.env)
                    stats = self._parse_feature_stats(result.stdout)
                    if progress_callback:
                        progress_callback(image_count, image_count)
                    logger.info(f"✅ Feature extraction succeeded with fallback parameters: {stats}")
                    return stats
                except subprocess.CalledProcessError as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error.stderr}")
            
            # Re-raise with full error details
            raise Exception(f"Feature extraction failed: {error_output}")
    
    def match_features(self, matching_type: str = "sequential", use_gpu: bool = True, quality: str = "medium", progress_callback=None) -> Dict:
        """
        Match features between images with geometric verification
        
        OPTIMIZED FOR >80% IMAGE OVERLAP:
        - Low quality: Sequential matching with overlap=20 (~20-30% coverage)
        - Medium quality: Sequential matching with overlap=50 (~50-70% coverage)
        - High quality: Exhaustive matching (100% overlap potential, matches ALL pairs)
        
        Reference: https://colmap.github.io/tutorial.html#feature-matching-and-geometric-verification
        
        Matching strategies per COLMAP tutorial:
        - sequential_matcher: Best for video sequences (ordered frames)
        - exhaustive_matcher: Best for unordered images (all pairs) - used for high quality
        - spatial_matcher: Best for geotagged images
        
        Geometric verification is automatic via RANSAC and stored in two_view_geometries table.
        
        Higher overlap = more feature matches = better reconstruction quality
        """
        # Override GPU flag if GPU not available
        actual_use_gpu = use_gpu and self.gpu_available
        gpu_mode = "GPU" if actual_use_gpu else "CPU"
        logger.info(f"Matching features with {matching_type} matcher (quality={quality}) using {gpu_mode}")
        
        # Quality-based match limits - OPTIMIZED FOR RTX 4090
        # Increased match counts for denser point clouds
        quality_params = {
            "low": {"max_num_matches": "65536"},     # 2x increase
            "medium": {"max_num_matches": "131072"}, # 2x increase  
            "high": {"max_num_matches": "262144"},   # 2x increase - RTX 4090 power
            "ultra": {"max_num_matches": "262144"}    # Maximum matches
        }
        match_params = quality_params.get(quality, quality_params["medium"])
        
        # Quality-based overlap strategy for >80% image overlap
        # Higher overlap = better reconstruction quality
        overlap_params = {
            "low": {
                "overlap": "20",  # Match 20 adjacent frames (~20-30% overlap)
                "use_exhaustive": False
            },
            "medium": {
                "overlap": "50",  # Match 50 adjacent frames (~50-70% overlap)
                "use_exhaustive": False
            },
            "high": {
                "overlap": "100",  # Match all frames with sequential (more reliable than exhaustive)
                "use_exhaustive": False  # Use sequential with high overlap for reliability
            },
            "ultra": {
                "overlap": "50",         # High overlap for sequential
                "use_exhaustive": True,  # FORCE exhaustive matching for Ultra
                "guided_matching": "1"   # Use geometric verification to guide matching
            }
        }
        overlap_config = overlap_params.get(quality, overlap_params["medium"])
        
        # Enhanced matching parameters for robust feature matching
        matching_base_params = [
            "--SiftMatching.max_ratio", "0.9",      # Loose ratio for more matches (RANSAC will clean up)
            "--SiftMatching.max_distance", "0.9",   # Allow distant matches
            "--SiftMatching.cross_check", "1",      # Keep cross-check for reliability
            "--SiftMatching.use_gpu", "1" if actual_use_gpu else "0",
            "--SiftMatching.gpu_index", "0",
            "--SiftMatching.max_num_matches", match_params["max_num_matches"],
            *(["--SiftMatching.guided_matching", "1"] if overlap_config.get("guided_matching") == "1" else [])
        ]
        
        # Matching strategy selection
        # Ultra quality: Try exhaustive first (maximum quality), fallback to sequential
        # High quality: Use sequential with high overlap (more reliable)
        # Medium/Low: Use sequential with moderate overlap
        if overlap_config["use_exhaustive"] or matching_type == "exhaustive":
            logger.info(f"🎯 Using EXHAUSTIVE matching for maximum overlap (quality={quality})")
            cmd = [
                "colmap", "exhaustive_matcher",
                "--database_path", str(self.database_path),
            ] + matching_base_params
        else:  # sequential_matcher with high overlap
            overlap_value = overlap_config["overlap"]
            logger.info(f"🎯 Using SEQUENTIAL matching with overlap={overlap_value} for reliable coverage (quality={quality})")
            cmd = [
                "colmap", "sequential_matcher",
                "--database_path", str(self.database_path),
                "--SequentialMatching.overlap", overlap_value,  # Match many adjacent frames for high overlap
            ] + matching_base_params
        
        try:
            # Estimate image pairs for progress tracking
            image_count = len(list(self.images_path.glob("*.jpg")))
            if overlap_config["use_exhaustive"]:
                # Exhaustive: n*(n-1)/2 pairs
                estimated_pairs = (image_count * (image_count - 1)) // 2
            else:
                # Sequential: overlap * image_count
                estimated_pairs = int(overlap_config["overlap"]) * image_count
            
            if progress_callback:
                progress_callback(0, estimated_pairs)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=self.env)
            
            # Parse match statistics
            stats = self._parse_match_stats(result.stdout)
            
            if progress_callback:
                progress_callback(estimated_pairs, estimated_pairs)
            
            logger.info(f"Feature matching complete: {stats}")
            return stats
            
        except subprocess.CalledProcessError as e:
            # Log full error details for debugging
            error_output = e.stderr if e.stderr else e.stdout if e.stdout else "No error output"
            logger.error(f"❌ Feature matching failed (exit code {e.returncode})")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Error output: {error_output}")
            
            # If GPU was attempted and failed, try CPU fallback
            if actual_use_gpu and ("GPU" in str(error_output) or "CUDA" in str(error_output)):
                logger.warning(f"⚠️  GPU feature matching failed, retrying with CPU...")
                self.gpu_available = False  # Disable GPU for future calls
                return self.match_features(matching_type=matching_type, use_gpu=False, quality=quality, progress_callback=progress_callback)
            
            # If exhaustive matching failed, try sequential matching as fallback
            if overlap_config["use_exhaustive"] or matching_type == "exhaustive":
                logger.warning(f"⚠️  Exhaustive matching failed, retrying with sequential matching (overlap=50)...")
                try:
                    # Fallback to sequential matching with moderate overlap
                    fallback_cmd = [
                        "colmap", "sequential_matcher",
                        "--database_path", str(self.database_path),
                        "--SequentialMatching.overlap", "50",  # Moderate overlap
                    ] + matching_base_params
                    
                    if progress_callback:
                        progress_callback(0, estimated_pairs)
                    
                    result = subprocess.run(fallback_cmd, check=True, capture_output=True, text=True, env=self.env)
                    stats = self._parse_match_stats(result.stdout)
                    
                    if progress_callback:
                        progress_callback(estimated_pairs, estimated_pairs)
                    
                    logger.info(f"✅ Feature matching succeeded with sequential fallback: {stats}")
                    return stats
                except subprocess.CalledProcessError as fallback_error:
                    logger.error(f"❌ Sequential fallback also failed: {fallback_error.stderr}")
            
            # Re-raise with full error details
            raise Exception(f"Feature matching failed: {error_output}")
    
    def dense_reconstruction(self, quality: str = "medium", progress_callback=None) -> Dict:
        """
        Dense Stereo Reconstruction
        Reference: https://colmap.github.io/tutorial.html#dense-reconstruction
        
        Process:
        1. Image undistortion - Prepare images for stereo
        2. Patch match stereo - Dense depth map estimation
        3. Stereo fusion - Fuse depth maps into dense point cloud
        
        Result: Much denser point cloud (10-100x more points than sparse)
        """
        logger.info(f"Starting dense reconstruction (quality={quality})")
        
        # Step 1: Image Undistortion
        # Undistort images using sparse reconstruction camera parameters
        logger.info("📸 Undistorting images...")
        if progress_callback:
            progress_callback("Undistorting images...", 0)
        undistorted_path = self.dense_path / "undistorted"
        
        undistort_cmd = [
            "colmap", "image_undistorter",
            "--image_path", str(self.images_path),
            "--input_path", str(self.sparse_path / "0"),  # Use model 0
            "--output_path", str(undistorted_path),
            "--output_type", "COLMAP"  # Keep COLMAP format
            # Note: max_image_size is set in patch_match_stereo, not here
        ]
        
        try:
            subprocess.run(undistort_cmd, check=True, capture_output=True, text=True, env=self.env)
            logger.info("✅ Image undistortion complete")
            if progress_callback:
                progress_callback("Undistortion complete", 33)
        except subprocess.CalledProcessError as e:
            logger.error(f"Image undistortion failed: {e.stderr}")
            raise
        
        # Step 2: Patch Match Stereo (Dense depth estimation)
        logger.info("🔍 Running patch match stereo...")
        if progress_callback:
            progress_callback("Patch match stereo...", 33)
        
        # Quality-based stereo parameters - OPTIMIZED FOR RTX 4090
        # RTX 4090 excels at parallel patch matching - maximize quality
        # Enhanced for 5M-20M point target (ultra quality)
        quality_params = {
            "low": {
                "window_radius": "5",       # Increased for better detail
                "window_step": "1",         # Decreased for denser sampling
                "num_samples": "15",        # 3x increase
                "num_iterations": "5",      # More refinement
                "geom_consistency_max_cost": "1.0",  # Stricter filtering
                "filter_min_ncc": "0.1",    # Normal filtering
                "cache_size": "64"          # GB - RTX 4090 has 24GB VRAM
            },
            "medium": {
                "window_radius": "7",       # Larger window for better matching
                "window_step": "1",         # Dense sampling
                "num_samples": "30",        # 2x increase
                "num_iterations": "7",      # More iterations = better quality
                "geom_consistency_max_cost": "0.6",  # Better filtering
                "filter_min_ncc": "0.2",    # Slightly stricter
                "cache_size": "64"
            },
            "high": {
                "window_radius": "11",      # Maximum detail capture
                "window_step": "1",         # Finest sampling
                "num_samples": "64",        # High sample count
                "num_iterations": "12",     # Good refinement
                "geom_consistency_max_cost": "1.0",  # LOOSE filtering for MORE points
                "filter_min_ncc": "0.05",   # LOOSE threshold for MORE points
                "cache_size": "64"          # Use all available VRAM
            },
            "ultra": {
                "window_radius": "15",      # Maximum detail
                "window_step": "1",         # Finest sampling
                "num_samples": "128",       # Extreme sampling
                "num_iterations": "15",     # Maximum refinement
                "geom_consistency_max_cost": "1.5",  # VERY LOOSE filtering for MAX density
                "filter_min_ncc": "0.02",   # ALMOST NO filtering - keep everything
                "cache_size": "64",         # Use all available VRAM
                "geom_consistency_regularizer": "0.1"  # Lower regularization
            }
        }
        stereo_params = quality_params.get(quality, quality_params["medium"])
        
        stereo_cmd = [
            "colmap", "patch_match_stereo",
            "--workspace_path", str(undistorted_path),
            "--workspace_format", "COLMAP",
            # CRITICAL: Prevent image downsampling - full resolution processing
            "--DenseMapperOptions.max_image_size", "0",  # 0 = no downsampling
            # Window parameters - control matching patch size
            "--PatchMatchStereo.window_radius", stereo_params["window_radius"],
            "--PatchMatchStereo.window_step", stereo_params["window_step"],
            # Sampling parameters - more samples = better quality
            "--PatchMatchStereo.num_samples", stereo_params["num_samples"],
            "--PatchMatchStereo.num_iterations", stereo_params["num_iterations"],
            # Geometric consistency filtering - removes outliers
            "--PatchMatchStereo.geom_consistency", "true",
            "--PatchMatchStereo.geom_consistency_max_cost", stereo_params["geom_consistency_max_cost"],
            # Enhanced geometric consistency for ultra quality
            *(["--PatchMatchStereo.geom_consistency_regularizer", stereo_params.get("geom_consistency_regularizer", "0.3")] 
              if quality == "ultra" else []),
            # NCC filtering - normalized cross correlation threshold
            "--PatchMatchStereo.filter", "true",
            "--PatchMatchStereo.filter_min_ncc", stereo_params["filter_min_ncc"],
            "--PatchMatchStereo.filter_min_triangulation_angle", "1.0",
            "--PatchMatchStereo.filter_min_num_consistent", "2",
            # Cache size - RTX 4090 has 24GB VRAM, use it!
            "--PatchMatchStereo.cache_size", stereo_params["cache_size"],
            # GPU configuration
            "--PatchMatchStereo.gpu_index", "-1" if not self.gpu_available else "0",
            "--PatchMatchStereo.allow_missing_files", "false"
        ]
        
        try:
            subprocess.run(stereo_cmd, check=True, capture_output=True, text=True, env=self.env)
            logger.info("✅ Patch match stereo complete")
            if progress_callback:
                progress_callback("Patch match stereo complete", 66)
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Patch match stereo failed: {e.stderr}")
            logger.warning("Skipping dense reconstruction, using sparse only")
            return {"status": "skipped", "reason": "stereo_failed"}
        
        # Step 3: Stereo Fusion (Create dense point cloud)
        logger.info("🔗 Fusing depth maps...")
        if progress_callback:
            progress_callback("Fusing depth maps...", 66)
        
        # Quality-based fusion parameters - fine-tuned for precision and density
        # Enhanced for 5M-20M point target (ultra quality)
        fusion_params = {
            "low": {
                "max_reproj_error": "2.0",      # Reduced for precision
                "max_depth_error": "0.015",      # Fine-tuned
                "max_normal_error": "12",        # Fine-tuned
                "min_num_pixels": "3"            # Lower = more points
            },
            "medium": {
                "max_reproj_error": "1.5",      # Reduced for better precision
                "max_depth_error": "0.012",      # Fine-tuned for accuracy
                "max_normal_error": "10",        # Fine-tuned
                "min_num_pixels": "3"            # Lower = more points
            },
            "high": {
                "max_reproj_error": "4.0",      # Relaxed for more points
                "max_depth_error": "0.05",       # Relaxed
                "max_normal_error": "20",         # Relaxed
                "min_num_pixels": "1"            # Minimum pixels
            },
            "ultra": {
                "max_reproj_error": "6.0",       # Extremely relaxed
                "max_depth_error": "0.1",      # Extremely relaxed
                "max_normal_error": "30",         # Extremely relaxed
                "min_num_pixels": "1",           # Minimum pixels
                "max_num_pixels": "10000",       # Maximum pixels per point
                "max_traversal_depth": "150"     # Deep traversal for coverage
            }
        }
        fusion_quality_params = fusion_params.get(quality, fusion_params["medium"])
        
        fusion_cmd = [
            "colmap", "stereo_fusion",
            "--workspace_path", str(undistorted_path),
            "--workspace_format", "COLMAP",
            "--input_type", "geometric",
            "--output_path", str(self.dense_path / "fused.ply"),
            # CRITICAL: Prevent image downsampling during fusion
            "--DenseMapperOptions.max_image_size", "0",  # 0 = no downsampling
            # OPTIMIZED FOR MAXIMUM DENSITY AND PRECISION - RTX 4090 can handle it
            "--StereoFusion.min_num_pixels", fusion_quality_params["min_num_pixels"],
            # Reduced reprojection error for more precise point fusion
            "--StereoFusion.max_reproj_error", fusion_quality_params["max_reproj_error"],
            # Fine-tuned depth error for better accuracy
            "--StereoFusion.max_depth_error", fusion_quality_params["max_depth_error"],
            # Fine-tuned normal error for better surface consistency
            "--StereoFusion.max_normal_error", fusion_quality_params["max_normal_error"],
            # Additional fusion parameters for better quality
            "--StereoFusion.check_num_images", "50",   # Check consistency across many images
            "--StereoFusion.use_cache", "true",        # Speed up with caching
            "--StereoFusion.cache_size", "32",         # GB cache for fusion
            # Ultra quality enhancements
            *(["--StereoFusion.max_num_pixels", fusion_quality_params.get("max_num_pixels", "10000"),
               "--StereoFusion.max_traversal_depth", fusion_quality_params.get("max_traversal_depth", "100")]
              if quality == "ultra" else [])
        ]
        
        try:
            subprocess.run(fusion_cmd, check=True, capture_output=True, text=True, env=self.env)
            logger.info("✅ Stereo fusion complete - Dense point cloud created")
            if progress_callback:
                progress_callback("Fusion complete", 100)
            
            # Check if dense point cloud exists
            dense_ply = self.dense_path / "fused.ply"
            if dense_ply.exists():
                return {
                    "status": "success",
                    "dense_ply": str(dense_ply),
                    "type": "dense"
                }
            else:
                return {"status": "no_output"}
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Stereo fusion failed: {e.stderr}")
            return {"status": "failed", "error": str(e)}
    
    def sparse_reconstruction(self, quality: str = "medium", progress_callback=None) -> Dict:
        """
        Incremental Structure-from-Motion reconstruction
        
        Reference: https://colmap.github.io/tutorial.html#sparse-reconstruction
        
        Process per COLMAP tutorial:
        1. Load extracted data from database into memory
        2. Seed reconstruction from an initial image pair
        3. Incrementally extend scene by registering new images
        4. Triangulate new 3D points
        5. Creates multiple models if not all images register into same model
        
        Output: Binary files in sparse/N/ directory:
        - cameras.bin: Camera intrinsics
        - images.bin: Camera poses (extrinsics)
        - points3D.bin: 3D points
        """
        logger.info(f"Starting sparse reconstruction (quality={quality})")
        
        # Quality-based mapper parameters - OPTIMIZED FOR RTX 4090
        # Stricter parameters = better sparse model = better dense reconstruction
        quality_params = {
            "low": {
                "init_min_num_inliers": "100",   # Doubled for better initialization
                "min_num_matches": "15",         # Higher minimum for stability
                "filter_max_reproj_error": "6.0", # Stricter filtering
                "min_tri_angle": "1.5",         # Minimum triangulation angle
            },
            "medium": {
                "init_min_num_inliers": "150",   # Higher for better quality
                "min_num_matches": "20",         # More matches required
                "filter_max_reproj_error": "4.0", # Tighter error threshold
                "min_tri_angle": "1.5",
            },
            "high": {
                "init_min_num_inliers": "200",   # Maximum quality initialization
                "min_num_matches": "30",         # Many matches for robustness
                "filter_max_reproj_error": "2.0", # Very strict for best quality
                "min_tri_angle": "1.5",
            },
            "ultra": {
                "init_min_num_inliers": "200",   # Maximum quality initialization
                "min_num_matches": "30",         # Many matches for robustness
                "filter_max_reproj_error": "2.0", # Very strict for best quality
                "min_tri_angle": "1.5",         # Minimum triangulation angle for stability
            }
        }
        mapper_params = quality_params.get(quality, quality_params["medium"])
        
        cmd = [
            "colmap", "mapper",
            "--database_path", str(self.database_path),
            "--image_path", str(self.images_path),
            "--output_path", str(self.sparse_path),
            
            # Thread Configuration - RTX 4090 systems typically have high-end CPUs
            "--Mapper.num_threads", "16",  # Increased for faster processing
            
            # Initialization
            "--Mapper.init_min_num_inliers", mapper_params["init_min_num_inliers"],
            "--Mapper.init_max_forward_motion", "0.95",
            "--Mapper.init_min_tri_angle", "16.0",
            
            # Bundle Adjustment (refinement)
            "--Mapper.ba_refine_focal_length", "1",      # Refine focal length
            "--Mapper.ba_refine_principal_point", "0",   # Keep principal point
            "--Mapper.ba_refine_extra_params", "1",      # Refine distortion
            
            # Bundle Adjustment Iterations - MORE REFINEMENT = BETTER QUALITY
            "--Mapper.ba_local_max_num_iterations", "50",   # Increased from 40
            "--Mapper.ba_global_max_num_iterations", "150", # Increased from 100
            "--Mapper.ba_global_max_refinements", "8",      # More global refinements
            
            # Point Filtering
            "--Mapper.filter_max_reproj_error", mapper_params["filter_max_reproj_error"],
            "--Mapper.filter_min_tri_angle", "1.5",  # Filter unstable points with small triangulation angles
            "--Mapper.min_num_matches", mapper_params["min_num_matches"],
            
            # Triangulation - filter unstable 3D points
            "--Mapper.tri_min_angle", "1.5",  # Minimum triangulation angle (degrees) for new points
            "--Mapper.tri_ignore_two_view_tracks", "0",  # Include 2-view tracks
            "--Mapper.tri_max_transitivity", "2",
            
            # Multiple Models (per COLMAP tutorial)
            "--Mapper.multiple_models", "1",
            "--Mapper.max_num_models", "10",  # Up to 10 models
            "--Mapper.max_model_overlap", "20",
            
            # Other Options
            "--Mapper.extract_colors", "1",  # RGB colors for points
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=self.env)
            
            # Parse reconstruction statistics
            stats = self._parse_reconstruction_stats(result.stdout)
            
            # Find best model (most 3D points)
            best_model, model_stats = self._find_best_model()
            logger.info(f"Sparse reconstruction complete: {stats}")
            
            return {
                "model_path": str(best_model) if best_model else None,
                "num_models": model_stats.get("num_models", 0),
                "best_model_points": model_stats.get("points_3d", 0),
                "stats": {**stats, **model_stats}
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Sparse reconstruction failed: {e.stderr}")
            raise
    
    def export_model(self, output_format: str = "PLY", model_dir: Optional[Path] = None) -> str:
        """
        Export reconstruction to various formats
        
        Reference: https://colmap.github.io/tutorial.html#importing-and-exporting
        
        Supported formats (per COLMAP tutorial):
        - PLY: Point cloud for visualization
        - TXT: Text format (cameras.txt, images.txt, points3D.txt)
        - BIN: Binary format (native)
        - NVM: VisualSFM format
        - Bundler: Bundler format
        - VRML: VRML format
        
        Exports the best sparse model to specified format.
        Following COLMAP convention, output goes to workspace root (job_path).
        """
        # Find best sparse model if not specified
        if model_dir is None:
            best_model, _ = self._find_best_model()
            if not best_model:
                raise ValueError("No reconstruction found to export")
            model_dir = best_model
        
        logger.info(f"Exporting model {model_dir} to {output_format} format")
        
        # Handle different output formats
        if output_format == "PLY":
            # Point cloud export
            output_file = self.job_path / "point_cloud.ply"
            
            cmd = [
                "colmap", "model_converter",
                "--input_path", str(model_dir),
                "--output_path", str(output_file),
                "--output_type", "PLY",
            ]
        elif output_format == "TXT":
            # Text format export (cameras.txt, images.txt, points3D.txt)
            output_dir = self.job_path / "model_text"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "colmap", "model_converter",
                "--input_path", str(model_dir),
                "--output_path", str(output_dir),
                "--output_type", "TXT",
            ]
            output_file = output_dir  # Directory for text format
        elif output_format == "BIN":
            # Binary format export
            output_dir = self.job_path / "model_binary"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "colmap", "model_converter",
                "--input_path", str(model_dir),
                "--output_path", str(output_dir),
                "--output_type", "BIN",
            ]
            output_file = output_dir  # Directory for binary format
        elif output_format == "NVM":
            # VisualSFM NVM format
            output_file = self.job_path / "model.nvm"
            
            cmd = [
                "colmap", "model_converter",
                "--input_path", str(model_dir),
                "--output_path", str(output_file),
                "--output_type", "NVM",
            ]
        else:
            raise ValueError(f"Unsupported export format: {output_format}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Exported model to {output_file} ({output_format} format)")
            return str(output_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Export failed: {e.stderr}")
            raise
    
    def export_point_cloud(self, output_format: str = "PLY") -> str:
        """
        Convenience wrapper for point cloud export
        """
        return self.export_model(output_format="PLY")
    
    def import_model(self, import_path: Path, input_format: str = "TXT") -> Path:
        """
        Import reconstruction from external format
        
        Reference: https://colmap.github.io/tutorial.html#importing-and-exporting
        
        Supported input formats:
        - TXT: Text format (cameras.txt, images.txt, points3D.txt)
        - BIN: Binary format (cameras.bin, images.bin, points3D.bin)
        - PLY: Point cloud (RGB only, no camera poses)
        
        Output: Imported model in sparse directory as new numbered model.
        """
        logger.info(f"Importing model from {import_path} ({input_format} format)")
        
        # Create import directory in sparse/
        sparse_dirs = sorted(self.sparse_path.glob("[0-9]*"))
        if sparse_dirs:
            next_model_id = max([int(d.name) for d in sparse_dirs]) + 1
        else:
            next_model_id = 0
        
        import_dir = self.sparse_path / str(next_model_id)
        import_dir.mkdir(parents=True, exist_ok=True)
        
        if input_format == "PLY":
            # PLY imports differently - no camera poses
            raise NotImplementedError("PLY import requires manual camera pose setup")
        
        cmd = [
            "colmap", "model_converter",
            "--input_path", str(import_path),
            "--input_type", input_format,
            "--output_path", str(import_dir),
            "--output_type", "BIN",
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Imported model to {import_dir}")
            return import_dir
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Import failed: {e.stderr}")
            raise
    
    def _find_best_model(self) -> Tuple[Optional[Path], Dict]:
        """
        Find the best sparse reconstruction model
        
        COLMAP creates multiple reconstructions (0/, 1/, etc.) when not all 
        images register into the same model. This function selects the model
        with the most 3D points as the best reconstruction.
        
        Reference: https://colmap.github.io/tutorial.html#sparse-reconstruction
        """
        sparse_dirs = sorted(self.sparse_path.glob("[0-9]*"))
        
        if not sparse_dirs:
            return None, {}
        
        best_model = sparse_dirs[0]  # Default to first
        best_points = 0
        
        for sparse_dir in sparse_dirs:
            points3d_file = sparse_dir / "points3D.bin"
            if points3d_file.exists():
                # Count points (approximate by file size)
                # Each point in binary format: id (uint64) + xyz (3x float32) + rgb (uint8x3) + error (float32) + 2x track (int64)
                # Total: 8 + 12 + 3 + 4 + 16 = ~43 bytes + alignment ≈ 48 bytes
                point_count = points3d_file.stat().st_size // 48
                if point_count > best_points:
                    best_points = point_count
                    best_model = sparse_dir
        
        stats = {
            "num_models": len(sparse_dirs),
            "points_3d": best_points,
            "model_id": best_model.name
        }
        
        logger.info(f"Found {len(sparse_dirs)} models, best is {best_model.name} with {best_points} points")
        return best_model, stats
    
    def _parse_feature_stats(self, output: str) -> Dict:
        """
        Parse feature extraction statistics from COLMAP output
        Extracts: num_images, total_features, avg_features_per_image
        """
        stats = {
            "status": "success" if "Database" in output else "unknown"
        }
        
        # Try to extract statistics from output
        lines = output.split('\n')
        for i, line in enumerate(lines):
            # Look for database stats
            if "Database:" in line and i + 1 < len(lines):
                # Next line often has image count
                try:
                    num_images = len(list(self.images_path.glob("*.jpg")))
                    stats["num_images"] = num_images
                except:
                    pass
                break
        
        # Count features in database
        try:
            if self.database_path.exists():
                import sqlite3
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                
                # Count keypoints
                cursor.execute("SELECT COUNT(*) FROM keypoints")
                stats["total_keypoints"] = cursor.fetchone()[0]
                
                # Count images
                cursor.execute("SELECT COUNT(*) FROM images")
                stats["num_images"] = cursor.fetchone()[0]
                
                if stats["num_images"] > 0:
                    stats["avg_features_per_image"] = stats["total_keypoints"] // stats["num_images"]
                
                conn.close()
                logger.info(f"Feature stats: {stats['num_images']} images, {stats['total_keypoints']} keypoints")
        except Exception as e:
            logger.warning(f"Could not parse feature stats from database: {e}")
        
        return stats
    
    def _parse_match_stats(self, output: str) -> Dict:
        """
        Parse feature matching statistics from COLMAP output
        Extracts: matched_pairs, verification_rate
        """
        stats = {
            "status": "success" if "Database" in output else "unknown"
        }
        
        # Try to extract statistics from output
        lines = output.split('\n')
        for line in lines:
            # Look for match count
            if "Matched" in line and "pairs" in line:
                try:
                    # Extract number from "Matched X image pairs"
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        stats["matched_pairs"] = int(match.group(1))
                except:
                    pass
        
        # Count matches in database
        try:
            if self.database_path.exists():
                import sqlite3
                conn = sqlite3.connect(self.database_path)
                cursor = conn.cursor()
                
                # Count two-view geometries (verified matches)
                cursor.execute("SELECT COUNT(*) FROM two_view_geometries")
                stats["verified_pairs"] = cursor.fetchone()[0]
                
                conn.close()
                logger.info(f"Match stats: {stats.get('verified_pairs', 'unknown')} verified pairs")
        except Exception as e:
            logger.warning(f"Could not parse match stats from database: {e}")
        
        return stats
    
    def _parse_reconstruction_stats(self, output: str) -> Dict:
        """
        Parse sparse reconstruction statistics from COLMAP output
        """
        stats = {
            "status": "success" if "Database" in output else "unknown"
        }
        
        # Try to extract statistics from output
        lines = output.split('\n')
        for line in lines:
            # Look for registered images
            if "Registered" in line and "images" in line:
                try:
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        stats["registered_images"] = int(match.group(1))
                except:
                    pass
            
            # Look for reconstructed points
            if "Reconstructed" in line and "points" in line:
                try:
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        stats["reconstructed_points"] = int(match.group(1))
                except:
                    pass
        
        return stats
    
    def inspect_database(self) -> Dict:
        """
        Inspect COLMAP database contents
        Reference: https://colmap.github.io/tutorial.html#database-management
        
        Returns comprehensive database statistics including:
        - Cameras (intrinsic parameters)
        - Images (metadata and registration status)
        - Keypoints (SIFT features per image)
        - Matches (feature correspondences)
        - Two-view geometries (geometrically verified matches)
        
        Optimizations:
        - SQLite WAL mode for better concurrency
        - Combined queries to reduce round trips
        - Memory-efficient row fetching
        """
        if not self.database_path.exists():
            logger.warning(f"Database not found at {self.database_path}")
            return {"status": "not_found", "message": "Database does not exist yet"}
        
        import sqlite3
        
        stats = {
            "status": "success",
            "database_path": str(self.database_path),
        }
        
        try:
            conn = sqlite3.connect(self.database_path)
            
            # Optimize SQLite for read performance
            # Enable Write-Ahead Logging (WAL) for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            # Increase page cache size (16MB)
            conn.execute("PRAGMA cache_size=-16384")
            # Use memory-mapped I/O for better performance
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            cursor = conn.cursor()
            
            # Get all camera information in one query
            cursor.execute("SELECT * FROM cameras LIMIT 100")
            cameras = cursor.fetchall()
            stats["num_cameras"] = cursor.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
            
            if cameras:
                stats["cameras"] = []
                for camera in cameras:
                    stats["cameras"].append({
                        "camera_id": camera[0],
                        "model": camera[1],
                        "width": camera[2],
                        "height": camera[3],
                        "params": camera[4]
                    })
            
            # Get all counts in combined query for efficiency
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM images) as num_images,
                    (SELECT COUNT(*) FROM keypoints) as num_keypoints,
                    (SELECT AVG(rows) FROM keypoints) as avg_keypoints,
                    (SELECT COUNT(*) FROM matches) as num_matches,
                    (SELECT AVG(rows) FROM matches) as avg_matches,
                    (SELECT COUNT(*) FROM two_view_geometries) as num_tvg
            """)
            counts = cursor.fetchone()
            
            stats["num_images"] = counts[0] or 0
            stats["num_keypoints"] = counts[1] or 0
            stats["avg_keypoints_per_image"] = round(counts[2], 2) if counts[2] else 0
            stats["num_matches"] = counts[3] or 0
            stats["avg_matches_per_pair"] = round(counts[4], 2) if counts[4] else 0
            stats["num_two_view_geometries"] = counts[5] or 0
            
            # Get top images (limit for performance)
            cursor.execute("SELECT name, camera_id FROM images LIMIT 50")
            images = cursor.fetchall()
            if images:
                stats["images"] = [{"name": img[0], "camera_id": img[1]} for img in images]
            
            # Get two-view geometry statistics
            cursor.execute("SELECT AVG(CAST(rows AS FLOAT)) FROM two_view_geometries WHERE rows > 0")
            avg_inliers = cursor.fetchone()[0]
            if avg_inliers:
                stats["avg_inliers_per_pair"] = round(avg_inliers, 2)
            
            # Calculate verification rate and inlier ratio in one query
            if stats["num_matches"] > 0:
                stats["verification_rate"] = round((stats["num_two_view_geometries"] / stats["num_matches"]) * 100, 2)
                
                # Optimized inlier ratio query with proper indexing
                cursor.execute("""
                    SELECT AVG(CAST(tvg.rows AS FLOAT) / CAST(m.rows AS FLOAT))
                    FROM two_view_geometries tvg 
                    JOIN matches m ON tvg.pair_id = m.pair_id 
                    WHERE m.rows > 0 AND tvg.rows > 0
                """)
                inlier_ratio = cursor.fetchone()[0]
                if inlier_ratio:
                    stats["avg_inlier_ratio"] = round(inlier_ratio * 100, 2)
            
            conn.close()
            
            logger.info(f"Database inspection complete: {stats['num_cameras']} cameras, {stats['num_images']} images, {stats['num_keypoints']} keypoints")
            
        except Exception as e:
            logger.error(f"Database inspection failed: {e}")
            stats["status"] = "error"
            stats["error"] = str(e)
        
        return stats
    
    def clean_database(self) -> Dict:
        """
        Clean COLMAP database by removing unused data
        Reference: https://colmap.github.io/tutorial.html#database-management
        
        Removes:
        - Images without features
        - Matches for deleted image pairs
        - Orphaned keypoints/descriptors
        
        Benefits:
        - Smaller file size
        - Faster processing
        - Cleaner data structure
        """
        if not self.database_path.exists():
            logger.warning(f"Database not found at {self.database_path}")
            return {"status": "not_found", "message": "Database does not exist yet"}
        
        try:
            import sqlite3
            import tempfile
            
            logger.info("Cleaning database...")
            
            # Create backup
            backup_path = self.database_path.with_suffix('.db.backup')
            shutil.copy2(self.database_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Use COLMAP database_cleaner
            # Reference: https://colmap.github.io/cli.html#database-cleaner
            cmd = [
                "colmap", "database_cleaner",
                "--database_path", str(self.database_path),
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't fail if database is already clean
            )
            
            if result.returncode == 0:
                logger.info("Database cleaned successfully")
                return {
                    "status": "success",
                    "message": "Database cleaned successfully",
                    "backup_path": str(backup_path)
                }
            else:
                logger.warning(f"Database cleaner returned {result.returncode}: {result.stderr}")
                # Restore backup
                shutil.copy2(backup_path, self.database_path)
                return {
                    "status": "warning",
                    "message": "Database may not need cleaning",
                    "output": result.stdout
                }
                
        except Exception as e:
            logger.error(f"Database cleaning failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_camera_for_image(self, image_name: str) -> Optional[Dict]:
        """
        Get camera parameters for a specific image
        Useful for sharing intrinsic parameters between images
        Reference: https://colmap.github.io/tutorial.html#database-management
        
        Returns camera model (PINHOLE, SIMPLE_PINHOLE, etc.) and parameters
        """
        if not self.database_path.exists():
            return None
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get image's camera_id
            cursor.execute("SELECT camera_id FROM images WHERE name = ?", (image_name,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return None
            
            camera_id = result[0]
            
            # Get camera details
            cursor.execute("SELECT * FROM cameras WHERE camera_id = ?", (camera_id,))
            camera = cursor.fetchone()
            
            conn.close()
            
            if camera:
                return {
                    "camera_id": camera[0],
                    "model": camera[1],
                    "width": camera[2],
                    "height": camera[3],
                    "params": camera[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get camera for image {image_name}: {e}")
            return None
    
    def set_camera_for_images(self, image_names: list, camera_id: int) -> Dict:
        """
        Set the same camera for multiple images
        Useful for sharing intrinsic parameters between images with same camera
        Reference: https://colmap.github.io/tutorial.html#database-management
        
        Args:
            image_names: List of image names to update
            camera_id: Camera ID to assign
        """
        if not self.database_path.exists():
            return {"status": "not_found", "message": "Database does not exist yet"}
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            updated_count = 0
            for image_name in image_names:
                cursor.execute("UPDATE images SET camera_id = ? WHERE name = ?", (camera_id, image_name))
                if cursor.rowcount > 0:
                    updated_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated camera for {updated_count} images")
            
            return {
                "status": "success",
                "updated_images": updated_count,
                "total_images": len(image_names)
            }
            
        except Exception as e:
            logger.error(f"Failed to set camera for images: {e}")
            return {"status": "error", "error": str(e)}


def process_video_to_pointcloud(
    job_id: str,
    video_path: str,
    quality: str = "medium",
    max_frames: int = 50
) -> Dict:
    """
    Complete pipeline: Video -> 3D Point Cloud
    """
    job_path = f"/workspace/{job_id}"
    processor = COLMAPProcessor(job_path)
    
    # Step 1: Extract frames
    frame_count = processor.extract_frames(video_path, max_frames=max_frames)
    
    # Step 2: Extract features (GPU accelerated)
    feature_stats = processor.extract_features(quality=quality, use_gpu=True)
    
    # Step 3: Match features (GPU accelerated)
    match_stats = processor.match_features(matching_type="sequential", use_gpu=True)
    
    # Step 4: Sparse reconstruction
    recon_result = processor.sparse_reconstruction()
    
    # Step 5: Export point cloud
    ply_file = processor.export_point_cloud(output_format="PLY")
    
    return {
        "job_id": job_id,
        "frame_count": frame_count,
        "feature_stats": feature_stats,
        "match_stats": match_stats,
        "reconstruction": recon_result,
        "output_file": ply_file
    }

