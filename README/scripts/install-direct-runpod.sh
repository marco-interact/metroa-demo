#!/bin/bash
# ============================================================================
# Direct Installation on RunPod (NO DOCKER)
# ============================================================================
# Installs COLMAP and dependencies directly on the RunPod container
# Build time: 2-3 minutes (vs 5-45 min for Docker)
# ============================================================================

set -e

echo "============================================================================"
echo "🚀 DIRECT INSTALLATION ON RUNPOD (NO DOCKER)"
echo "============================================================================"
echo ""
echo "This installs everything directly without Docker"
echo "⏱️  Time: 2-3 minutes"
echo "💾 Space: ~2 GB"
echo ""

cd /workspace/metroa-demo

# ============================================================================
# Step 1: Install System Dependencies
# ============================================================================
echo "============================================================================"
echo "📦 Step 1: Installing System Dependencies"
echo "============================================================================"
echo ""

echo "Installing COLMAP, FFmpeg, and libraries..."
apt-get update -qq
apt-get install -y -qq \
    colmap \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    sqlite3 \
    lsof \
    curl \
    > /dev/null 2>&1

echo "✅ System dependencies installed"
echo ""

# Verify COLMAP
echo "🔍 Verifying COLMAP..."
if colmap --version > /dev/null 2>&1; then
    COLMAP_VERSION=$(colmap --version 2>&1 | head -1)
    echo "✅ COLMAP installed: $COLMAP_VERSION"
else
    echo "❌ COLMAP installation failed"
    exit 1
fi
echo ""

# ============================================================================
# Step 2: Install Python Dependencies
# ============================================================================
echo "============================================================================"
echo "🐍 Step 2: Installing Python Dependencies"
echo "============================================================================"
echo ""

echo "Installing Python packages..."
pip install -q -r requirements.txt

echo "✅ Python dependencies installed"
echo ""

# Verify key packages
echo "🔍 Verifying Python packages..."
python -c "
import sys
try:
    import fastapi
    import open3d
    import cv2
    import numpy
    print('✅ FastAPI:', fastapi.__version__)
    print('✅ Open3D:', open3d.__version__)
    print('✅ OpenCV: OK')
    print('✅ NumPy: OK')
except Exception as e:
    print(f'❌ Package verification failed: {e}')
    sys.exit(1)
"
echo ""

# ============================================================================
# Step 3: Create Directories
# ============================================================================
echo "============================================================================"
echo "📁 Step 3: Creating Data Directories"
echo "============================================================================"
echo ""

mkdir -p data/{uploads,results,cache}
mkdir -p logs

echo "✅ Directories created"
echo ""

# ============================================================================
# Step 4: Test Imports
# ============================================================================
echo "============================================================================"
echo "🧪 Step 4: Testing Backend Imports"
echo "============================================================================"
echo ""

python -c "
import sys
try:
    from colmap_processor import COLMAPProcessor
    from colmap_binary_parser import COLMAPBinaryParser
    from quality_presets import get_preset
    from pointcloud_postprocess import postprocess_pointcloud
    print('✅ All backend imports successful')
except Exception as e:
    print(f'❌ Import test failed: {e}')
    sys.exit(1)
"
echo ""

# ============================================================================
# Step 5: Check GPU
# ============================================================================
echo "============================================================================"
echo "🎮 Step 5: Checking GPU"
echo "============================================================================"
echo ""

if nvidia-smi > /dev/null 2>&1; then
    echo "✅ GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
else
    echo "⚠️  No GPU detected (COLMAP will use CPU)"
fi
echo ""

# ============================================================================
# SUCCESS
# ============================================================================
echo "============================================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "============================================================================"
echo ""
echo "🚀 Start the backend:"
echo ""
echo "  # Option 1: Run directly"
echo "  python main.py"
echo ""
echo "  # Option 2: Run in screen (persistent)"
echo "  screen -S metroa-backend -d -m bash -c 'cd /workspace/metroa-demo && python main.py'"
echo ""
echo "🧪 Test the backend:"
echo ""
echo "  curl http://localhost:8888/health"
echo ""
echo "📊 What was installed:"
echo "  ✅ COLMAP (GPU-enabled)"
echo "  ✅ FFmpeg (video processing)"
echo "  ✅ Python 3.12 + FastAPI"
echo "  ✅ Open3D (point cloud processing)"
echo "  ✅ All dependencies"
echo ""
echo "🌐 Access URLs:"
echo "  Local:        http://localhost:8888"
echo "  RunPod Proxy: https://$(hostname)-8888.proxy.runpod.net"
echo ""
echo "============================================================================"
echo ""

