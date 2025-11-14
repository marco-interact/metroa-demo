# Fix OpenMVS VCG Build Error

## Quick Fix for Current Pod

If OpenMVS build failed with "VCG required, but not found", run these commands:

```bash
cd /workspace/openMVS

# Verify VCG submodule
if [ ! -d "vcg" ]; then
    echo "Cloning VCG manually..."
    git submodule update --init --recursive --force
fi

# Check VCG structure
echo "VCG structure:"
ls -la vcg/ | head -10

# Determine correct VCG path
VCG_PATH=""
if [ -d "vcg/vcg" ]; then
    # VCG is in vcg/vcg subdirectory - VCG_ROOT should point to parent
    VCG_PATH="/workspace/openMVS/vcg"
    echo "Found VCG in vcg/vcg subdirectory"
elif [ -d "vcg" ]; then
    VCG_PATH="/workspace/openMVS/vcg"
    echo "Found VCG in vcg directory"
else
    echo "ERROR: VCG not found!"
    exit 1
fi

# Set VCG_ROOT environment variable (REQUIRED by OpenMVS CMake)
export VCG_ROOT="${VCG_PATH}"
echo "Set VCG_ROOT=${VCG_ROOT}"

# Clean previous CMake attempt
cd build
rm -rf CMakeCache.txt CMakeFiles/

# Find OpenCV path
OPENCV_DIR=$(pkg-config --variable=prefix opencv4 2>/dev/null || pkg-config --variable=prefix opencv 2>/dev/null || echo "/usr")

# Reconfigure CMake with VCG_ROOT
cmake /workspace/openMVS \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DVCG_DIR="${VCG_ROOT}" \
    -DOpenCV_DIR="${OPENCV_DIR}/lib/cmake/opencv4" \
    -DCMAKE_CXX_FLAGS="-O3"

# Build
make -j8
make install
ldconfig

# Verify installation
/usr/local/bin/OpenMVS/DensifyPointCloud --help | head -3
```

## What Was Fixed

The OpenMVS CMake configuration requires the `VCG_ROOT` environment variable to be set, not just the `VCG_DIR` CMake variable. The updated script now:

1. ✅ Sets `VCG_ROOT` environment variable
2. ✅ Checks for `vcg/vcg` subdirectory structure
3. ✅ Adjusts `VCG_ROOT` to parent if `vcg/vcg` exists
4. ✅ Uses both `VCG_DIR` CMake variable and `VCG_ROOT` env var

## Updated Script

The `setup-metroa-pod.sh` script has been updated with these fixes. Pull the latest code:

```bash
cd /workspace/metroa-demo
git pull origin main
```

Then either:
- Restart the setup script: `bash setup-metroa-pod.sh`
- Or continue the current build with the quick fix above

