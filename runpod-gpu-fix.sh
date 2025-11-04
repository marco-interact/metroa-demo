#!/bin/bash
################################################################################
# RunPod GPU-Enabled COLMAP Headless Setup
# Fixes SIGABRT crashes while leveraging RTX 4090
################################################################################

set -e

echo "=========================================="
echo "🚀 Configuring COLMAP for GPU Acceleration"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Install headless display dependencies
echo -e "${BLUE}📦 Installing headless display dependencies...${NC}"
apt-get update && apt-get install -y \
    xvfb \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    libgl1-mesa-glx \
    libgomp1 \
    libomp-dev \
    mesa-utils \
    libglx0 \
    libglu1-mesa

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 2: Check GPU availability
echo -e "${BLUE}🎮 Checking GPU...${NC}"
if nvidia-smi > /dev/null 2>&1; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo -e "${GREEN}✅ GPU detected${NC}"
else
    echo -e "${YELLOW}⚠️  No GPU detected${NC}"
fi
echo ""

# Step 3: Kill existing processes
echo -e "${BLUE}🔄 Restarting services...${NC}"
killall python3 2>/dev/null || true
killall Xvfb 2>/dev/null || true
sleep 2

# Step 4: Start virtual display
echo -e "${BLUE}🖥️  Starting virtual framebuffer...${NC}"
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &
XVFB_PID=$!
sleep 2

# Verify Xvfb is running
if ps -p $XVFB_PID > /dev/null; then
    echo -e "${GREEN}✅ Xvfb started (PID: $XVFB_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Xvfb may not be running properly${NC}"
fi
echo ""

# Step 5: Update backend startup script with GPU configuration
echo -e "${BLUE}📝 Creating GPU-enabled startup script...${NC}"
cat > /workspace/start-colmap-gpu.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting COLMAP Backend with GPU Acceleration..."

# Start Xvfb if not running
if ! pgrep Xvfb > /dev/null; then
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &
    sleep 2
fi

# Navigate to project
cd /workspace/colmap-demo
source venv/bin/activate

# GPU and Display Configuration
export DISPLAY=:99
export QT_QPA_PLATFORM=offscreen
export MESA_GL_VERSION_OVERRIDE=3.3
export LIBGL_ALWAYS_SOFTWARE=0

# CUDA Configuration for RTX 4090
export CUDA_VISIBLE_DEVICES=0
export CUDA_DEVICE_ORDER=PCI_BUS_ID

# Application Configuration
export STORAGE_DIR=/workspace/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/data/cache
export UPLOADS_DIR=/workspace/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Kill existing server
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start server
echo "✅ Backend starting on http://0.0.0.0:8000"
echo "🌐 Public URL: https://xhqt6a1roo8mrc-8000.proxy.runpod.net"
echo "🎮 GPU: Enabled (RTX 4090)"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/server.log 2>&1 &

echo "Server started with PID: $!"
echo "View logs: tail -f /workspace/server.log"
EOF

chmod +x /workspace/start-colmap-gpu.sh
echo -e "${GREEN}✅ Startup script created${NC}"
echo ""

# Step 6: Pull latest code
echo -e "${BLUE}📥 Pulling latest code from GitHub...${NC}"
cd /workspace/colmap-demo
git pull origin main
echo ""

# Step 7: Start the backend
echo -e "${BLUE}🚀 Starting backend with GPU configuration...${NC}"
/workspace/start-colmap-gpu.sh &
sleep 5

# Step 8: Verify
echo ""
echo -e "${BLUE}🧪 Testing backend...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Backend is running!${NC}"
    echo "$HEALTH"
else
    echo -e "${YELLOW}⚠️  Backend may be starting up. Check logs:${NC}"
    echo "tail -f /workspace/server.log"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ GPU Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  • GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo "  • Display: Xvfb :99 (Headless)"
echo "  • COLMAP: GPU-accelerated"
echo "  • Backend: https://xhqt6a1roo8mrc-8000.proxy.runpod.net"
echo ""
echo "🔄 Restart: /workspace/start-colmap-gpu.sh"
echo "📝 Logs: tail -f /workspace/server.log"
echo "🎮 GPU Status: nvidia-smi"
echo ""

