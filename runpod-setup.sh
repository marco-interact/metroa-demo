#!/bin/bash
################################################################################
# RunPod COLMAP Setup Script
# Pod: xhqt6a1roo8mrc (colmap_worker_gpu)
# Storage: rrtms4xkiz (colmap-gpu-volume)
# Date: 2025-11-03
################################################################################

set -e  # Exit on error

echo "=================================================="
echo "🚀 Starting RunPod COLMAP Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC}  $1"
}

################################################################################
# Step 1: System Update and Dependencies
################################################################################

print_step "Step 1/7: Updating system and installing dependencies..."

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
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    python3-pip \
    sqlite3 \
    unzip

print_info "✅ System dependencies installed"

################################################################################
# Step 2: Install COLMAP
################################################################################

print_step "Step 2/7: Installing COLMAP..."

cd /workspace

# Check if COLMAP is already installed
if command -v colmap &> /dev/null; then
    print_info "COLMAP already installed: $(colmap -h | head -n 1)"
else
    # Clone and build COLMAP from source
    if [ ! -d "colmap" ]; then
        git clone https://github.com/colmap/colmap.git
    fi
    
    cd colmap
    mkdir -p build && cd build
    
    cmake .. -GNinja \
        -DCMAKE_CUDA_ARCHITECTURES=native \
        -DCMAKE_BUILD_TYPE=Release
    
    ninja && ninja install
    
    print_info "✅ COLMAP installed successfully"
fi

################################################################################
# Step 3: Clone Application Repository
################################################################################

print_step "Step 3/7: Cloning application repository..."

cd /workspace

if [ -d "colmap-demo" ]; then
    print_info "Repository already exists, pulling latest changes..."
    cd colmap-demo
    git pull origin main
else
    git clone https://github.com/marco-interact/colmap-demo.git
    cd colmap-demo
    print_info "✅ Repository cloned"
fi

################################################################################
# Step 4: Setup Python Environment
################################################################################

print_step "Step 4/7: Setting up Python environment..."

cd /workspace/colmap-demo

# Create virtual environment if it doesn't exist
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
# Step 5: Create Directories and Set Environment Variables
################################################################################

print_step "Step 5/7: Creating directories and setting environment..."

# Create necessary directories
mkdir -p data/results data/cache data/uploads

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Add environment variables to .bashrc if not already present
if ! grep -q "COLMAP Application Environment" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# COLMAP Application Environment
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1
EOF
    print_info "✅ Environment variables added to .bashrc"
fi

# Also add COLMAP to PATH if not already there
if ! grep -q "colmap/bin" ~/.bashrc; then
    echo 'export PATH="/workspace/colmap/bin:$PATH"' >> ~/.bashrc
fi

source ~/.bashrc

print_info "✅ Directories created and environment configured"

################################################################################
# Step 6: Initialize Database
################################################################################

print_step "Step 6/7: Initializing database..."

cd /workspace/colmap-demo
source venv/bin/activate

python3 << 'PYEOF'
import asyncio
from database import Database

async def init_db():
    db = Database()
    await db.initialize()
    print('✅ Database initialized successfully!')

asyncio.run(init_db())
PYEOF

################################################################################
# Step 7: Create Startup Script
################################################################################

print_step "Step 7/7: Creating startup script..."

cat > /workspace/start-colmap.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting COLMAP Backend Server..."

# Navigate to project
cd /workspace/colmap-demo

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the backend server
echo "✅ Backend starting on http://0.0.0.0:8000"
echo "🌐 Public URL: http://xhqt6a1roo8mrc-8000.proxy.runpod.net"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x /workspace/start-colmap.sh

print_info "✅ Startup script created at /workspace/start-colmap.sh"

################################################################################
# Setup Complete
################################################################################

echo ""
echo "=================================================="
echo "✨ Setup Complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start the backend server:"
echo "   /workspace/start-colmap.sh"
echo ""
echo "2. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. Access the public endpoint:"
echo "   http://xhqt6a1roo8mrc-8000.proxy.runpod.net"
echo ""
echo "4. Deploy frontend to Vercel:"
echo "   cd /workspace/colmap-demo"
echo "   npm install && npm run build"
echo "   vercel --prod --scope interact-hq"
echo ""
echo "📚 Documentation: /workspace/colmap-demo/cursor-logs/2025-11-03/"
echo ""
echo "=================================================="
echo ""

# Test installations
print_step "Testing installations..."
echo ""
echo "COLMAP Version:"
colmap -h | head -n 1
echo ""
echo "Python Version:"
python3 --version
echo ""
echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo ""
echo "=================================================="

