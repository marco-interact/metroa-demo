# COLMAP Utils Installation

## Overview

The [colmap_utils](https://github.com/uzh-rpg/colmap_utils) repository has been integrated into the metroa-demo project as a **git submodule**. This provides additional utilities for working with COLMAP, including:

- Reconstructing SfM models from posed images
- Registering/localizing images against existing SfM models
- Computing localization errors
- Visualizing matched landmarks
- Extracting 3D point information

## Installation Status

✅ **Repository cloned**: `colmap_utils/` directory (git submodule)  
✅ **Dependencies added**: `tqdm` and `torch` added to `requirements.txt`  
✅ **Python path**: Can be imported as `from colmap_utils.utils import colmap_utils`

## Initial Setup

### Clone with Submodule

If you're cloning the repository fresh:

```bash
git clone --recursive https://github.com/marco-interact/metroa-demo.git
```

Or if you already cloned without submodules:

```bash
git submodule update --init --recursive
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` - Array operations
- `torch` - PyTorch for custom feature matching  
- `tqdm` - Progress bars

## Usage

### Import in Python

```python
import sys
sys.path.insert(0, '/path/to/metroa-demo')
from colmap_utils.utils import colmap_utils
from colmap_utils.utils import colmap_read_model
from colmap_utils.utils import exp_utils
```

### Available Scripts

All scripts are located in the `colmap_utils/` directory:

- `reconstruct_from_known_poses.py` - Build SfM model from posed images
- `register_images_to_model.py` - Localize new images against existing model
- `generate_img_rel_path.py` - Generate image path files for localization
- `calculate_pose_errors.py` - Compute localization errors
- `viz_matched_landmarks.py` - Visualize matched landmarks
- `strip_points3d.py` - Extract 3D point positions
- `calculate_point_view_direction.py` - Calculate view directions

### Example: Using colmap_utils in metroa-demo

```python
from colmap_utils.utils.colmap_utils import (
    getImgNameToImgIdMap,
    addImagesToDatabase,
    extractFeatures,
    matchFeatures
)

# Use in your COLMAP processing pipeline
database_path = "/workspace/data/results/scan_id/database.db"
img_name_to_id = getImgNameToImgIdMap(database_path)
```

## RunPod Setup

When setting up on RunPod, make sure to initialize submodules:

```bash
cd /workspace/metroa-demo
git submodule update --init --recursive
pip install --break-system-packages -r requirements.txt
```

## Documentation

For detailed usage instructions, see:
- [colmap_utils README](colmap_utils/README.md)
- [Original Repository](https://github.com/uzh-rpg/colmap_utils)

## Integration Notes

- The `colmap_utils` directory is a git submodule at the project root
- Scripts can be run directly: `python colmap_utils/reconstruct_from_known_poses.py --help`
- Utils can be imported in Python code: `from colmap_utils.utils import colmap_utils`
- Compatible with existing COLMAP installation
