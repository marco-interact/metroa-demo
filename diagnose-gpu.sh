#!/bin/bash
################################################################################
# GPU and COLMAP Diagnostics for RunPod
# Checks GPU availability, CUDA, and COLMAP GPU support
################################################################################

echo "=================================================="
echo "🔍 GPU and COLMAP Diagnostics"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_check() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

################################################################################
# Check 1: GPU Detection
################################################################################

echo "==> Check 1: GPU Detection"
echo ""

if command -v nvidia-smi &> /dev/null; then
    print_check "nvidia-smi found"
    echo ""
    nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader
    echo ""
else
    print_error "nvidia-smi not found!"
    exit 1
fi

################################################################################
# Check 2: CUDA Installation
################################################################################

echo "==> Check 2: CUDA Installation"
echo ""

if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep release | awk '{print $6}' | cut -c2-)
    print_check "CUDA found: version $CUDA_VERSION"
    nvcc --version | grep release
else
    print_warn "nvcc not found - CUDA may not be installed"
fi
echo ""

# Check for CUDA libraries
if [ -d "/usr/local/cuda" ]; then
    print_check "CUDA directory exists: /usr/local/cuda"
    ls -la /usr/local/cuda/lib64/libcudart.so* 2>/dev/null || print_warn "CUDA runtime libraries not found"
else
    print_warn "CUDA directory not found at /usr/local/cuda"
fi
echo ""

################################################################################
# Check 3: COLMAP Installation
################################################################################

echo "==> Check 3: COLMAP Installation"
echo ""

if command -v colmap &> /dev/null; then
    print_check "COLMAP found: $(which colmap)"
    
    # Check COLMAP version
    COLMAP_VERSION=$(colmap -h 2>&1 | head -n 1)
    echo "   Version: $COLMAP_VERSION"
    
    # Check if COLMAP was built with CUDA
    echo ""
    echo "Checking COLMAP build configuration..."
    
    if colmap -h 2>&1 | grep -i "cuda" > /dev/null; then
        print_check "COLMAP mentions CUDA in help"
    else
        print_warn "COLMAP help doesn't mention CUDA"
    fi
    
    # Try to check if COLMAP binary has CUDA symbols
    if ldd $(which colmap) | grep -i cuda > /dev/null 2>&1; then
        print_check "COLMAP is linked with CUDA libraries:"
        ldd $(which colmap) | grep -i cuda
    else
        print_error "COLMAP is NOT linked with CUDA libraries!"
        echo ""
        echo "This is likely why GPU processing fails."
        echo "COLMAP needs to be rebuilt with CUDA support."
    fi
else
    print_error "COLMAP not found!"
    exit 1
fi
echo ""

################################################################################
# Check 4: Test COLMAP GPU Feature
################################################################################

echo "==> Check 4: Test COLMAP GPU Feature Extraction"
echo ""

# Create a temporary test directory
TEST_DIR="/tmp/colmap_gpu_test_$$"
mkdir -p "$TEST_DIR/images"

# Create a simple test image
convert -size 640x480 xc:white "$TEST_DIR/images/test.jpg" 2>/dev/null || {
    # If ImageMagick not available, use a simple pattern
    dd if=/dev/urandom of="$TEST_DIR/images/test.jpg" bs=1024 count=100 2>/dev/null
}

echo "Testing GPU feature extraction..."

# Try GPU feature extraction
if colmap feature_extractor \
    --database_path "$TEST_DIR/database.db" \
    --image_path "$TEST_DIR/images" \
    --SiftExtraction.use_gpu 1 \
    --SiftExtraction.max_num_features 1000 \
    > "$TEST_DIR/gpu_test.log" 2>&1; then
    print_check "GPU feature extraction works!"
    GPU_WORKS=true
else
    print_error "GPU feature extraction failed!"
    echo "Error log:"
    cat "$TEST_DIR/gpu_test.log"
    GPU_WORKS=false
fi
echo ""

# Try CPU feature extraction for comparison
echo "Testing CPU feature extraction..."
if colmap feature_extractor \
    --database_path "$TEST_DIR/database_cpu.db" \
    --image_path "$TEST_DIR/images" \
    --SiftExtraction.use_gpu 0 \
    --SiftExtraction.max_num_features 1000 \
    > "$TEST_DIR/cpu_test.log" 2>&1; then
    print_check "CPU feature extraction works!"
else
    print_error "CPU feature extraction also failed!"
    cat "$TEST_DIR/cpu_test.log"
fi
echo ""

# Cleanup
rm -rf "$TEST_DIR"

################################################################################
# Summary and Recommendations
################################################################################

echo "=================================================="
echo "📋 Summary and Recommendations"
echo "=================================================="
echo ""

if [ "$GPU_WORKS" = true ]; then
    print_check "GPU is working correctly!"
    echo ""
    echo "Your COLMAP is properly configured for GPU processing."
    echo "The previous error might have been temporary."
else
    print_error "GPU processing is NOT working"
    echo ""
    echo "Possible causes:"
    echo "1. COLMAP was not built with CUDA support"
    echo "2. CUDA libraries are missing or incompatible"
    echo "3. GPU drivers are outdated"
    echo ""
    echo "Solutions:"
    echo ""
    echo "Option 1: Rebuild COLMAP with CUDA support"
    echo "   Run: bash /workspace/colmap-demo/build-colmap-gpu.sh"
    echo ""
    echo "Option 2: Use CPU processing (slower but reliable)"
    echo "   Backend will automatically fallback to CPU"
    echo ""
fi

echo "=================================================="

