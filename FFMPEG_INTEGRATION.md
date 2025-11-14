# FFmpeg Integration Status

## ✅ FFmpeg Integration Overview

**Status:** ✅ **CORRECTLY INTEGRATED AND WORKING**

[FFmpeg](https://www.ffmpeg.org/) is properly integrated into the Metroa Labs pipeline for video processing and frame extraction.

---

## Installation

### Setup Script (`setup-metroa-pod.sh`)
- ✅ FFmpeg installed via `apt-get install -y ffmpeg` (Step 1/9)
- ✅ Installed from Ubuntu repositories (typically FFmpeg 4.x or 5.x)
- ✅ Available system-wide on `/usr/bin/ffmpeg` and `/usr/bin/ffprobe`

### Dockerfile
- ✅ FFmpeg included in base image dependencies
- ✅ Available in production Docker image

---

## Usage in Codebase

### 1. Frame Extraction (`colmap_processor.py`)

**Function:** `extract_frames()`

**FFmpeg Command:**
```python
cmd = [
    "ffmpeg", "-i", video_path,
    "-vf", f"fps={actual_fps},scale={scale}",
    "-q:v", "2",  # High quality JPEG (1-31, lower = better)
    "-y",  # Overwrite existing files
    str(output_pattern)
]
```

**Features:**
- ✅ **Auto FPS Detection** - Uses `ffprobe` to analyze video duration
- ✅ **Quality-based Scaling** - Adjusts resolution based on quality preset
- ✅ **Progress Tracking** - Callbacks for UI updates
- ✅ **Error Handling** - Proper exception handling with error messages

**Quality Presets:**
- `low`: 1280px max width
- `medium`: 1920px max width  
- `high`: 3840px max width

### 2. Video Metadata Detection (`colmap_processor.py`)

**Function:** `_auto_detect_optimal_fps()`

**FFprobe Command:**
```python
probe_cmd = [
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    str(video_path)
]
```

**Purpose:**
- Detects video duration
- Calculates optimal FPS for target frame count
- Balances quality vs processing speed

### 3. 360° Video Detection (`video_360_converter.py`)

**Function:** `detect_360_video()`

**FFprobe Command:**
```python
cmd = [
    "ffprobe", "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,display_aspect_ratio",
    "-of", "json",
    str(video_path)
]
```

**Purpose:**
- Detects equirectangular 360° videos
- Analyzes aspect ratio (2:1 = 360°)
- Returns video metadata (width, height, format)

---

## FFmpeg Features Used

### ✅ Currently Used:
1. **Video Decoding** - `-i` input option
2. **Frame Rate Filter** - `fps={fps}` filter
3. **Scaling Filter** - `scale={width}:-2` (maintains aspect ratio)
4. **JPEG Quality** - `-q:v 2` (high quality)
5. **Frame Limiting** - `-frames:v {count}` (optional)
6. **Metadata Extraction** - `ffprobe` for video analysis
7. **JSON Output** - `-of json` for structured data

### 🔄 Could Be Enhanced (Future):
1. **Hardware Acceleration** - GPU-accelerated decoding (NVIDIA NVENC/NVDEC)
2. **Multi-threaded Processing** - `-threads` option for parallel processing
3. **Better Codec Support** - Explicit codec selection
4. **Progress Reporting** - `-progress` option for real-time progress
5. **Error Resilience** - `-err_detect` for better error handling

---

## Best Practices Followed

### ✅ Current Implementation:
- ✅ Uses `subprocess.run()` with `check=True` for error handling
- ✅ Captures stderr for error messages
- ✅ Uses `-v error` for minimal ffprobe output
- ✅ Uses `-y` flag to avoid prompts
- ✅ Maintains aspect ratio with `scale={width}:-2`
- ✅ High quality JPEG output (`-q:v 2`)

### ⚠️ Potential Improvements:
1. **Version Verification** - Check FFmpeg version on startup
2. **Feature Detection** - Verify required codecs/filters are available
3. **Progress Reporting** - Use `-progress` for better progress tracking
4. **Hardware Acceleration** - Enable GPU decoding for faster processing

---

## Error Handling

### Current Implementation:
```python
try:
    subprocess.run(cmd, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    logger.error(f"Frame extraction failed: {e.stderr}")
    raise
```

**Status:** ✅ Proper error handling with logging

---

## Performance Considerations

### Current Settings:
- **JPEG Quality:** `-q:v 2` (high quality, larger files)
- **Scaling:** Quality-based (1280px - 3840px)
- **FPS:** Auto-detected based on video length

### Optimization Opportunities:
1. **GPU Acceleration** - Use NVIDIA NVENC/NVDEC for faster decoding
2. **Parallel Processing** - Use `-threads` for multi-core extraction
3. **Lower Quality for Preview** - Use `-q:v 5` for faster processing (optional)

---

## Verification Commands

### Check FFmpeg Installation:
```bash
# Check version
ffmpeg -version

# Check codecs
ffmpeg -codecs | grep -i h264

# Check filters
ffmpeg -filters | grep -i scale
```

### Test Frame Extraction:
```bash
# Extract frames from test video
ffmpeg -i test.mp4 -vf "fps=2,scale=1920:-2" -q:v 2 frame_%06d.jpg

# Get video duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 test.mp4
```

---

## Integration Points

### Pipeline Flow:
```
Video Upload
    ↓
FFprobe: Detect video metadata (duration, resolution, format)
    ↓
FFmpeg: Extract frames at optimal FPS
    ↓
COLMAP: Process frames for 3D reconstruction
```

### Code Locations:
- **Frame Extraction:** `colmap_processor.py::extract_frames()`
- **FPS Detection:** `colmap_processor.py::_auto_detect_optimal_fps()`
- **360° Detection:** `video_360_converter.py::detect_360_video()`

---

## Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| **Installation** | ✅ Working | Installed via apt-get |
| **Frame Extraction** | ✅ Working | Uses fps and scale filters |
| **Metadata Detection** | ✅ Working | Uses ffprobe for analysis |
| **360° Video Support** | ✅ Working | Detects equirectangular format |
| **Error Handling** | ✅ Working | Proper exception handling |
| **Progress Tracking** | ✅ Working | Callbacks for UI updates |
| **Hardware Acceleration** | ⚠️ Not Used | Could enable GPU decoding |
| **Version Verification** | ⚠️ Not Done | Could check on startup |

**Overall:** ✅ **FFmpeg is correctly integrated and working as expected.**

---

## Recommendations

### Short-term (Optional):
1. Add FFmpeg version check on startup
2. Verify required codecs are available
3. Add hardware acceleration support (NVIDIA NVENC)

### Long-term (Future):
1. Use FFmpeg's `-progress` option for better progress reporting
2. Implement adaptive quality based on video codec
3. Add support for more video formats (AV1, VVC)

---

## References

- [FFmpeg Official Website](https://www.ffmpeg.org/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [FFmpeg Filters](https://ffmpeg.org/ffmpeg-filters.html)
- [FFprobe Documentation](https://ffmpeg.org/ffprobe.html)

