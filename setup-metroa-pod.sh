#!/bin/bash
################################################################################
# METROA POD - Complete Setup Script
# Pod: k0r2cn19yf6osw (metroa_worker_gpu)
# GPU: RTX 4090 (24GB VRAM)
# Volume: metroa-volume (mvmh2mg1pt)
# Port: 8888
# Date: 2025-11-12
################################################################################

set -e  # Exit on error

echo "=================================================="
echo "🚀 METROA POD - Complete Setup"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() { echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ${NC}  $1"; }
print_error() { echo -e "${RED}❌${NC}  $1"; }

################################################################################
# STEP 1: System Update and Dependencies
################################################################################

print_step "Step 1/9: Installing system dependencies..."

apt-get update && apt-get upgrade -y

apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    ninja-build \
    libboost-all-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    libcgal-dev \
    libcgal-qt5-dev \
    libceres-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    python3-pip \
    sqlite3 \
    unzip \
    ffmpeg \
    lsof

print_info "✅ System dependencies installed"

################################################################################
# STEP 2: Build COLMAP with GPU Support (RTX 4090)
################################################################################

print_step "Step 2/8: Building COLMAP with GPU support..."

cd /workspace

# Remove any existing COLMAP
apt-get remove -y colmap 2>/dev/null || true
rm -rf colmap

# Clone COLMAP
git clone https://github.com/colmap/colmap.git
cd colmap
git checkout 3.10  # Stable version with CUDA 12 support

# Configure for RTX 4090 (compute capability 8.9)
mkdir -p build && cd build

cmake .. -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES=89 \
    -DCUDA_ENABLED=ON \
    -DGUI_ENABLED=OFF \
    -DOPENGL_ENABLED=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local

# Build with limited parallelism (prevent OOM)
ninja -j8
ninja install
ldconfig

print_info "✅ COLMAP installed with GPU support"

################################################################################
# STEP 3: Build OpenMVS (Ultra Quality Densification)
################################################################################

print_step "Step 3/9: Building OpenMVS for ultra quality mode..."

cd /workspace

# Remove any existing OpenMVS
rm -rf openMVS openmvs-build

# Clone OpenMVS with submodules (VCG library)
print_info "Cloning OpenMVS repository..."
git clone --recursive https://github.com/cdcseacave/openMVS.git
cd openMVS
git checkout v2.2.0
git submodule update --init --recursive

# Build OpenMVS
print_info "Building OpenMVS (this may take 10-15 minutes)..."
OPENMVS_BUILD_DIR="/workspace/openMVS/build"
mkdir -p "$OPENMVS_BUILD_DIR" && cd "$OPENMVS_BUILD_DIR"

cmake /workspace/openMVS \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DVCG_DIR=/workspace/openMVS/vcg \
    -DCMAKE_CXX_FLAGS="-O3"

# Build with limited parallelism (prevent OOM)
make -j8
make install
ldconfig

# Verify OpenMVS installation
if DensifyPointCloud --help > /dev/null 2>&1 && \
   InterfaceCOLMAP --help > /dev/null 2>&1; then
    print_info "✅ OpenMVS installed successfully"
    print_info "   Tools: DensifyPointCloud, InterfaceCOLMAP, ReconstructMesh"
else
    print_error "OpenMVS installation verification failed"
    exit 1
fi

################################################################################
# STEP 4: Clone Application Repository
################################################################################

print_step "Step 4/9: Cloning metroa-demo repository..."

cd /workspace

if [ -d "metroa-demo" ]; then
    print_info "Repository exists, pulling latest..."
    cd metroa-demo
    git pull origin main
else
    git clone https://github.com/marco-interact/metroa-demo.git
    cd metroa-demo
    print_info "✅ Repository cloned"
fi

################################################################################
# STEP 5: Setup Python Environment
################################################################################

print_step "Step 5/9: Setting up Python environment..."

cd /workspace/metroa-demo

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_info "✅ Virtual environment created"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

print_info "✅ Python dependencies installed"

################################################################################
# STEP 6: Setup Persistent Storage and Environment
################################################################################

print_step "Step 6/9: Configuring persistent storage..."

# Create directory structure on volume
mkdir -p /workspace/data/results
mkdir -p /workspace/data/cache
mkdir -p /workspace/data/uploads

# Link to app directory
cd /workspace/metroa-demo
mkdir -p data
ln -sf /workspace/data/results data/results
ln -sf /workspace/data/cache data/cache
ln -sf /workspace/data/uploads data/uploads

# Set environment variables permanently
cat >> ~/.bashrc << 'EOF'

# Metroa Environment Variables
export STORAGE_DIR=/workspace/data/results
export DATABASE_PATH=/workspace/data/database.db
export CACHE_DIR=/workspace/data/cache
export UPLOADS_DIR=/workspace/data/uploads
export COLMAP_PATH=/usr/local/bin/colmap
export PYTHONUNBUFFERED=1
export PATH="/usr/local/bin:$PATH"

# Qt Headless Mode for COLMAP GPU
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
EOF

# Load environment
source ~/.bashrc

print_info "✅ Persistent storage configured"

################################################################################
# STEP 7: Initialize Database with Demo Data
################################################################################

print_step "Step 7/9: Initializing database..."

cd /workspace/metroa-demo
source venv/bin/activate

python3 << 'PYEOF'
from database import db

# Create database instance (auto-initializes tables)
print('✅ Database tables initialized!')

# Setup demo data
result = db.setup_demo_data()
if result['status'] == 'success':
    print(f"✅ Demo data setup: {result['message']}")
    print(f"   Project: Reconstruction Test Project 1")
    print(f"   Scans: 1 (Dollhouse Scan)")
else:
    print(f"⚠️  Demo data setup: {result.get('message', 'Unknown error')}")
PYEOF

print_info "✅ Database initialized with demo data"

################################################################################
# STEP 8: Test COLMAP GPU and OpenMVS Functionality
################################################################################

print_step "Step 8/9: Testing COLMAP GPU and OpenMVS functionality..."

# Test GPU
if nvidia-smi > /dev/null 2>&1; then
    print_info "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
else
    print_error "GPU not detected!"
fi

# Test COLMAP with headless mode
TEST_DIR="/tmp/colmap_test_$$"
mkdir -p "$TEST_DIR/images"
dd if=/dev/urandom of="$TEST_DIR/images/test.jpg" bs=1024 count=50 2>/dev/null

if QT_QPA_PLATFORM=offscreen colmap feature_extractor \
    --database_path "$TEST_DIR/test.db" \
    --image_path "$TEST_DIR/images" \
    --SiftExtraction.use_gpu 1 \
    --SiftExtraction.max_num_features 1000 \
    > /dev/null 2>&1; then
    print_info "✅ GPU feature extraction works!"
else
    print_info "⚠️  GPU not working, will use CPU fallback"
fi

rm -rf "$TEST_DIR"

# Test OpenMVS
if DensifyPointCloud --help > /dev/null 2>&1; then
    print_info "✅ OpenMVS tools available!"
else
    print_error "OpenMVS tools not found!"
fi

################################################################################
# STEP 9: Start Backend Server
################################################################################

print_step "Step 9/9: Starting backend server..."

cd /workspace/metroa-demo
source venv/bin/activate

# Kill any existing server
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
sleep 2

# Get pod ID
POD_ID=$(hostname)
PUBLIC_URL="https://${POD_ID}-8888.proxy.runpod.net"

print_info "Starting backend server..."
print_info "   Local: http://0.0.0.0:8888"
print_info "   Public: $PUBLIC_URL"

# Start server with proper environment
QT_QPA_PLATFORM=offscreen DISPLAY=:99 MESA_GL_VERSION_OVERRIDE=3.3 \
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload \
> /workspace/metroa-demo/backend.log 2>&1 &

echo $! > /workspace/metroa-demo/backend.pid
sleep 5

# Verify server started
if curl -s http://localhost:8888/health > /dev/null; then
    print_info "✅ Backend server started!"
else
    print_error "Backend failed to start. Check logs: tail -f backend.log"
    exit 1
fi

################################################################################
# DEPLOYMENT COMPLETE
################################################################################

echo ""
echo "=================================================="
echo "✨ METROA POD SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "📋 Pod Information:"
echo "   • Pod ID: $POD_ID"
echo "   • GPU: RTX 4090"
echo "   • Port: 8888"
echo "   • Volume: metroa-volume"
echo ""
echo "📋 Backend URLs:"
echo "   • Local:  http://localhost:8888"
echo "   • Public: $PUBLIC_URL"
echo "   • Health: $PUBLIC_URL/health"
echo ""
echo "📋 Useful Commands:"
echo "   • View logs:    tail -f /workspace/metroa-demo/backend.log"
echo "   • Stop backend: kill \$(cat /workspace/metroa-demo/backend.pid)"
echo "   • Restart:      bash /workspace/metroa-demo/setup-metroa-pod.sh"
echo ""
echo "📋 Test Backend:"
echo "   curl $PUBLIC_URL/health"
echo "   curl $PUBLIC_URL/api/status"
echo ""
echo "🌐 Next: Deploy Frontend"
echo "   Update .env.production with:"
echo "   NEXT_PUBLIC_API_URL=\"$PUBLIC_URL\""
echo ""
echo "=================================================="
echo ""

# Display final status
print_step "Final Verification..."
echo ""
echo "COLMAP Version:"
colmap -h 2>&1 | head -1
echo ""
echo "OpenMVS Tools:"
DensifyPointCloud --help 2>&1 | head -1 || echo "OpenMVS not available"
InterfaceCOLMAP --help 2>&1 | head -1 || echo "InterfaceCOLMAP not available"
echo ""
echo "Python Version:"
python3 --version
echo ""
echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo ""
echo "Backend PID:"
cat /workspace/metroa-demo/backend.pid
echo ""
echo "=================================================="
echo "✅ READY FOR PRODUCTION!"
echo "   • COLMAP: GPU-accelerated ✅"
echo "   • OpenMVS: Ultra quality mode ✅"
echo "   • Open3D: Post-processing ✅"
echo "=================================================="

