#!/bin/bash
################################################################################
# Build COLMAP from Source with GPU Support for RTX 4090
# This provides proper CUDA acceleration and headless operation
################################################################################

set -e

echo "=========================================="
echo "🔨 Building COLMAP with GPU Support"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Remove old COLMAP
echo -e "${BLUE}🗑️  Removing apt-installed COLMAP...${NC}"
apt-get remove -y colmap 2>/dev/null || true
rm -f /usr/bin/colmap /usr/local/bin/colmap

# Step 2: Install build dependencies
echo -e "${BLUE}📦 Installing build dependencies...${NC}"
apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 3: Check CUDA
echo -e "${BLUE}🎮 Checking CUDA installation...${NC}"
if nvcc --version > /dev/null 2>&1; then
    nvcc --version | head -1
    echo -e "${GREEN}✅ CUDA detected${NC}"
else
    echo -e "${YELLOW}⚠️  NVCC not found in PATH. Checking /usr/local/cuda...${NC}"
    if [ -d "/usr/local/cuda" ]; then
        export PATH="/usr/local/cuda/bin:$PATH"
        export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
        echo -e "${GREEN}✅ CUDA found at /usr/local/cuda${NC}"
    else
        echo -e "${YELLOW}⚠️  CUDA not found. Building without GPU support.${NC}"
    fi
fi
echo ""

# Step 4: Clone COLMAP
echo -e "${BLUE}📥 Cloning COLMAP...${NC}"
cd /workspace

if [ -d "colmap" ]; then
    echo "Removing old COLMAP source..."
    rm -rf colmap
fi

git clone https://github.com/colmap/colmap.git
cd colmap

# Use stable version
echo -e "${BLUE}📌 Checking out stable version 3.9.1...${NC}"
git checkout 3.9.1

echo -e "${GREEN}✅ COLMAP source ready${NC}"
echo ""

# Step 5: Configure build
echo -e "${BLUE}⚙️  Configuring CMake...${NC}"
mkdir -p build
cd build

# Detect CUDA capability for RTX 4090 (compute capability 8.9)
if nvcc --version > /dev/null 2>&1; then
    echo -e "${GREEN}Building with CUDA support for RTX 4090 (compute capability 8.9)${NC}"
    cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CUDA_ARCHITECTURES=89 \
        -DCUDA_ENABLED=ON \
        -DGUI_ENABLED=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local
else
    echo -e "${YELLOW}Building without CUDA support${NC}"
    cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCUDA_ENABLED=OFF \
        -DGUI_ENABLED=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local
fi

echo -e "${GREEN}✅ CMake configuration complete${NC}"
echo ""

# Step 6: Build
echo -e "${BLUE}🔨 Building COLMAP (this takes ~20 minutes)...${NC}"
echo -e "${YELLOW}☕ Good time for a coffee break!${NC}"
echo ""

# Build with progress
ninja -v

echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# Step 7: Install
echo -e "${BLUE}📦 Installing COLMAP...${NC}"
ninja install

echo -e "${GREEN}✅ COLMAP installed${NC}"
echo ""

# Step 8: Verify installation
echo -e "${BLUE}✔️  Verifying installation...${NC}"
COLMAP_PATH=$(which colmap)
if [ -z "$COLMAP_PATH" ]; then
    echo -e "${YELLOW}⚠️  colmap not in PATH, adding /usr/local/bin${NC}"
    export PATH="/usr/local/bin:$PATH"
    COLMAP_PATH=$(which colmap)
fi

echo "COLMAP location: $COLMAP_PATH"
echo ""

# Test COLMAP
echo -e "${BLUE}🧪 Testing COLMAP...${NC}"
colmap -h | head -5
echo ""

# Check GPU support
if colmap -h | grep -q "SiftExtraction.use_gpu"; then
    echo -e "${GREEN}✅ GPU support available${NC}"
else
    echo -e "${YELLOW}⚠️  GPU support may not be available${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ COLMAP Build Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  • COLMAP Version: 3.9.1"
echo "  • Installation: $COLMAP_PATH"
echo "  • GPU: $(if nvcc --version > /dev/null 2>&1; then echo "Enabled (RTX 4090)"; else echo "Disabled"; fi)"
echo "  • GUI: Disabled (Headless)"
echo ""
echo "🔄 Next steps:"
echo "1. Update environment:"
echo "   export COLMAP_PATH=\$(which colmap)"
echo ""
echo "2. Restart backend:"
echo "   /workspace/start-colmap-gpu.sh"
echo ""
echo "3. Test:"
echo "   colmap -h"
echo ""


