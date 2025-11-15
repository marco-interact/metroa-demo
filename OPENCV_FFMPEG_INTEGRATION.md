# OpenCV & FFmpeg Integration Analysis

## Executive Summary

**Recommendation**: 
- ✅ **Keep current OpenCV setup** (opencv-python from PyPI is sufficient)
- ✅ **Add FFmpeg v360 filter** for efficient 360° frame extraction
- ⚠️ **Consider opencv-contrib-python** if additional modules needed

## OpenCV Python Repository Analysis

### Repository Purpose
The [opencv-python repository](https://github.com/opencv/opencv-python) is **NOT a feature library** - it's a **build system** that:
- Creates precompiled OpenCV wheels for PyPI
- Handles CI/CD for multiple platforms
- Manages OpenCV submodules (opencv, opencv_contrib, opencv_extra)

### Current Metroa Usage
```python
# requirements.txt
opencv-python==4.10.0.84  # ✅ Already using official PyPI package
```

**What we're using OpenCV for:**
1. ✅ 360° video detection (`ffprobe` + aspect ratio heuristics)
2. ✅ Equirectangular to perspective conversion (`cv2.remap()`)
3. ✅ Image processing in OpenCV SfM pipeline
4. ✅ General computer vision operations

### Integration Options

#### Option 1: Keep Standard opencv-python ✅ RECOMMENDED
**Current**: `opencv-python==4.10.0.84`
- ✅ Precompiled wheels (fast installation)
- ✅ All core OpenCV features
- ✅ Sufficient for our use cases
- ✅ No build required

**Action**: No changes needed

#### Option 2: Switch to opencv-contrib-python ⚠️ OPTIONAL
**Package**: `opencv-contrib-python==4.10.0.84`
- ✅ Additional modules (SIFT, SURF, extra features)
- ⚠️ Larger package size
- ⚠️ May not be needed (we use COLMAP for features)

**When to use**: If we need:
- Additional feature detectors
- Extra computer vision algorithms
- Extended functionality

**Current need**: ❌ Not required - COLMAP handles feature detection

#### Option 3: Custom Build from opencv-python Repo ❌ NOT RECOMMENDED
**Why not**:
- ⚠️ Requires building from source (hours)
- ⚠️ Complex CMake configuration
- ⚠️ Platform-specific issues
- ✅ Pre-built wheels are sufficient

**When to use**: Only if we need:
- Specific CMake flags
- Custom patches
- Experimental features

## FFmpeg v360 Filter Analysis

### Provided Command
```python
command = [
    "ffmpeg",
    "-ss", str(time),
    "-i", video_path,
    "-vf", "v360=input=e:output=e",
    "-frames:v", "1",
    output_filename
]
subprocess.run(command, check=True)
```

### Analysis

**What it does:**
- Extracts **single frame** at specific `time`
- Uses `v360` filter with `input=e:output=e` (equirectangular → equirectangular)
- **No conversion** - keeps original 360° format
- Outputs single image file

**Use cases:**
1. ✅ **Thumbnail generation** - Extract preview frame
2. ✅ **Frame preview** - Show user what frame looks like
3. ✅ **Metadata extraction** - Get frame for analysis
4. ❌ **NOT for COLMAP** - We need perspective conversion

### Current Metroa Implementation

**What we currently do:**
```python
# video_360_converter.py
# 1. Detect 360° video
detection = detect_360_video(video_path)

# 2. Convert to perspective frames (for COLMAP)
convert_360_video_to_perspective_frames(
    video_path, output_dir,
    fov=90.0, num_views=8  # Multiple perspective views
)
```

**What we're missing:**
- ❌ Efficient single-frame extraction
- ❌ Thumbnail generation from 360° videos
- ❌ Preview frame extraction

## Recommended Integration

### 1. Add FFmpeg v360 Helper Function ✅

```python
# video_360_converter.py

def extract_360_frame(
    video_path: str,
    output_path: Path,
    time_seconds: float = 0.0,
    keep_equirectangular: bool = True
) -> Path:
    """
    Extract a single frame from 360° video
    
    Args:
        video_path: Input 360° video
        output_path: Output image path
        time_seconds: Time position in video (default: 0.0 = first frame)
        keep_equirectangular: If True, keep equirectangular format; 
                             If False, convert to perspective
    
    Returns:
        Path to extracted frame
    """
    if keep_equirectangular:
        # Use v360 filter to keep equirectangular format
        cmd = [
            "ffmpeg",
            "-ss", str(time_seconds),
            "-i", str(video_path),
            "-vf", "v360=input=e:output=e",
            "-frames:v", "1",
            "-y",  # Overwrite
            str(output_path)
        ]
    else:
        # Convert to perspective (single view)
        cmd = [
            "ffmpeg",
            "-ss", str(time_seconds),
            "-i", str(video_path),
            "-vf", "v360=input=e:output=perspective:pitch=0:yaw=0:fov=90",
            "-frames:v", "1",
            "-y",
            str(output_path)
        ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
```

### 2. Enhance Thumbnail Generation ✅

```python
# thumbnail_generator.py

def generate_360_thumbnail(
    video_path: str,
    output_path: Path,
    time_seconds: float = 1.0
) -> Path:
    """
    Generate thumbnail from 360° video
    
    Uses FFmpeg v360 filter for efficient extraction
    """
    from video_360_converter import extract_360_frame
    
    # Extract frame at specified time
    frame_path = output_path.parent / f"temp_frame_{time_seconds}.jpg"
    extract_360_frame(video_path, frame_path, time_seconds, keep_equirectangular=True)
    
    # Resize to thumbnail size
    import cv2
    img = cv2.imread(str(frame_path))
    thumbnail = cv2.resize(img, (640, 320))  # 2:1 aspect ratio
    cv2.imwrite(str(output_path), thumbnail)
    
    # Cleanup temp file
    frame_path.unlink()
    
    return output_path
```

### 3. Add Preview Frame Extraction ✅

```python
# colmap_processor.py

def extract_preview_frame(
    self,
    video_path: str,
    time_seconds: float = 1.0
) -> Optional[Path]:
    """
    Extract preview frame for user preview
    
    Returns equirectangular frame (not converted)
    """
    if not HAS_360_SUPPORT:
        return None
    
    try:
        detection = detect_360_video(video_path)
        if not detection.get('is_360', False):
            return None
        
        preview_path = self.job_path / "preview_360.jpg"
        from video_360_converter import extract_360_frame
        
        extract_360_frame(
            video_path,
            preview_path,
            time_seconds=time_seconds,
            keep_equirectangular=True
        )
        
        return preview_path
    except Exception as e:
        logger.warning(f"Could not extract preview frame: {e}")
        return None
```

## Benefits

### FFmpeg v360 Integration
1. ✅ **Efficient** - Hardware-accelerated when available
2. ✅ **Fast** - Single frame extraction in milliseconds
3. ✅ **Flexible** - Can extract equirectangular or perspective
4. ✅ **Standard** - Uses FFmpeg's built-in v360 filter

### OpenCV Status
1. ✅ **Already optimal** - Using official PyPI package
2. ✅ **No changes needed** - Current version sufficient
3. ⚠️ **Future consideration** - opencv-contrib-python if needed

## Implementation Plan

### Phase 1: Add FFmpeg v360 Helper (1 hour)
- [ ] Add `extract_360_frame()` to `video_360_converter.py`
- [ ] Test with sample 360° videos
- [ ] Document usage

### Phase 2: Enhance Thumbnail Generation (1 hour)
- [ ] Update `thumbnail_generator.py` to use v360 filter
- [ ] Support both standard and 360° videos
- [ ] Test thumbnail generation

### Phase 3: Add Preview Frame Extraction (1 hour)
- [ ] Add preview extraction to `colmap_processor.py`
- [ ] Expose via API endpoint
- [ ] Update frontend to show preview

**Total effort**: ~3 hours

## Code Examples

### Extract Single Frame (Equirectangular)
```python
from video_360_converter import extract_360_frame
from pathlib import Path

# Extract frame at 5 seconds, keep equirectangular format
frame = extract_360_frame(
    video_path="video_360.mp4",
    output_path=Path("frame_5s.jpg"),
    time_seconds=5.0,
    keep_equirectangular=True
)
```

### Extract Single Frame (Perspective)
```python
# Extract frame at 5 seconds, convert to perspective
frame = extract_360_frame(
    video_path="video_360.mp4",
    output_path=Path("frame_5s_perspective.jpg"),
    time_seconds=5.0,
    keep_equirectangular=False  # Convert to perspective
)
```

### Generate Thumbnail
```python
from thumbnail_generator import generate_360_thumbnail

thumbnail = generate_360_thumbnail(
    video_path="video_360.mp4",
    output_path=Path("thumbnail.jpg"),
    time_seconds=1.0
)
```

## Conclusion

### OpenCV
- ✅ **No changes needed** - Current setup is optimal
- ✅ **Standard package sufficient** - opencv-python from PyPI
- ⚠️ **Future**: Consider opencv-contrib-python if additional modules needed

### FFmpeg v360 Filter
- ✅ **Highly useful** - Efficient single-frame extraction
- ✅ **Should integrate** - Better than current approach for thumbnails/previews
- ✅ **Low effort** - Simple function addition

## References

- [OpenCV Python Repository](https://github.com/opencv/opencv-python)
- [FFmpeg v360 Filter Documentation](https://ffmpeg.org/ffmpeg-filters.html#v360)
- Current Implementation: `video_360_converter.py`
- Current Thumbnail: `thumbnail_generator.py`

