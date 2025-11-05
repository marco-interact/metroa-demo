#!/bin/bash
################################################################################
# Build COLMAP with GPU Support - Fixed for RTX 4090 + CUDA 12.8
# Optimized for headless operation on RunPod
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
RED='\033[0;31m'
NC='\033[0m'

################################################################################
# Step 1: Clean up old COLMAP
################################################################################

echo -e "${BLUE}🗑️  Removing old COLMAP...${NC}"
apt-get remove -y colmap 2>/dev/null || true
rm -f /usr/bin/colmap /usr/local/bin/colmap
rm -rf /workspace/colmap

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

################################################################################
# Step 2: Install dependencies
################################################################################

echo -e "${BLUE}📦 Installing dependencies...${NC}"
apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-regex-dev \
    libboost-atomic-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    libcgal-dev \
    libceres-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

################################################################################
# Step 3: Setup CUDA paths
################################################################################

echo -e "${BLUE}🎮 Setting up CUDA...${NC}"
export PATH="/usr/local/cuda/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
export CUDA_HOME="/usr/local/cuda"

if nvcc --version > /dev/null 2>&1; then
    CUDA_VERSION=$(nvcc --version | grep release | awk '{print $6}' | cut -c2-)
    echo -e "${GREEN}✅ CUDA $CUDA_VERSION detected${NC}"
    nvcc --version | head -1
else
    echo -e "${RED}❌ CUDA not found!${NC}"
    exit 1
fi
echo ""

################################################################################
# Step 4: Clone COLMAP (latest stable)
################################################################################

echo -e "${BLUE}📥 Cloning COLMAP...${NC}"
cd /workspace

git clone https://github.com/colmap/colmap.git
cd colmap

# Use latest stable release (3.10)
echo -e "${BLUE}📌 Checking out version 3.10...${NC}"
git checkout 3.10

echo -e "${GREEN}✅ COLMAP source ready${NC}"
echo ""

################################################################################
# Step 5: Configure CMake for headless GPU build
################################################################################

echo -e "${BLUE}⚙️  Configuring CMake for RTX 4090...${NC}"
mkdir -p build
cd build

# RTX 4090 compute capability: 8.9
cmake .. -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES=89 \
    -DCUDA_ENABLED=ON \
    -DGUI_ENABLED=OFF \
    -DOPENGL_ENABLED=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
    -DCMAKE_C_FLAGS="-O3" \
    -DCMAKE_CXX_FLAGS="-O3"

echo -e "${GREEN}✅ CMake configuration complete${NC}"
echo ""

################################################################################
# Step 6: Build with limited parallelism (avoid memory issues)
################################################################################

echo -e "${BLUE}🔨 Building COLMAP...${NC}"
echo -e "${YELLOW}⏱  This will take 15-20 minutes${NC}"
echo -e "${YELLOW}☕ Good time for a coffee!${NC}"
echo ""

# Use fewer jobs to avoid running out of memory
# 21 vCPU but limit to 8 jobs to avoid OOM
ninja -j8

echo -e "${GREEN}✅ Build complete${NC}"
echo ""

################################################################################
# Step 7: Install
################################################################################

echo -e "${BLUE}📦 Installing COLMAP to /usr/local...${NC}"
ninja install

# Update library cache
ldconfig

echo -e "${GREEN}✅ COLMAP installed${NC}"
echo ""

################################################################################
# Step 8: Verify installation
################################################################################

echo -e "${BLUE}✔️  Verifying installation...${NC}"

# Make sure it's in PATH
export PATH="/usr/local/bin:$PATH"

if ! command -v colmap &> /dev/null; then
    echo -e "${RED}❌ COLMAP not found in PATH${NC}"
    exit 1
fi

COLMAP_PATH=$(which colmap)
echo "COLMAP location: $COLMAP_PATH"
echo ""

# Show version
echo -e "${BLUE}📋 COLMAP Version:${NC}"
colmap -h 2>&1 | head -1
echo ""

# Check if linked with CUDA
echo -e "${BLUE}🔗 Checking CUDA linkage:${NC}"
if ldd $COLMAP_PATH | grep -q cuda; then
    echo -e "${GREEN}✅ COLMAP is linked with CUDA:${NC}"
    ldd $COLMAP_PATH | grep cuda | head -5
else
    echo -e "${RED}❌ COLMAP is NOT linked with CUDA${NC}"
    echo "This means GPU acceleration won't work!"
fi
echo ""

################################################################################
# Step 9: Test GPU functionality
################################################################################

echo -e "${BLUE}🧪 Testing GPU functionality...${NC}"

# Create test directory
TEST_DIR="/tmp/colmap_test_$$"
mkdir -p "$TEST_DIR/images"

# Create a simple test image
dd if=/dev/urandom of="$TEST_DIR/images/test.jpg" bs=1024 count=100 2>/dev/null

# Test GPU feature extraction
echo "Testing GPU feature extraction..."
if QT_QPA_PLATFORM=offscreen DISPLAY=:99 colmap feature_extractor \
    --database_path "$TEST_DIR/database.db" \
    --image_path "$TEST_DIR/images" \
    --SiftExtraction.use_gpu 1 \
    --SiftExtraction.max_num_features 1000 \
    > "$TEST_DIR/test.log" 2>&1; then
    echo -e "${GREEN}✅ GPU feature extraction works!${NC}"
else
    echo -e "${RED}❌ GPU feature extraction failed${NC}"
    echo "Error log:"
    cat "$TEST_DIR/test.log"
fi

# Cleanup
rm -rf "$TEST_DIR"
echo ""

################################################################################
# Summary
################################################################################

echo "=========================================="
echo -e "${GREEN}✨ COLMAP Build Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  • COLMAP Version: 3.10"
echo "  • Location: $COLMAP_PATH"
echo "  • CUDA: $(nvcc --version | grep release | awk '{print $6}')"
echo "  • GPU: RTX 4090 (compute 8.9)"
echo "  • GUI: Disabled (headless)"
echo ""
echo "🔄 Next steps:"
echo ""
echo "1. Restart backend:"
echo "   cd /workspace/colmap-demo"
echo "   bash resume-runpod.sh"
echo ""
echo "2. Backend will now use GPU acceleration!"
echo ""
echo "=========================================="

