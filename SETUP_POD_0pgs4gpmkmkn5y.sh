#!/bin/bash
set -e

echo "🚀 Setting up Pod: colmap_worker_gpu (0pgs4gpmkmkn5y)"
echo "=================================================="

# Verify volume mount
echo ""
echo "1️⃣ Verifying volume mount..."
mount | grep /workspace || echo "⚠️  WARNING: /workspace may not be on persistent volume"
df -h /workspace

# Update system
echo ""
echo "2️⃣ Updating system packages..."
apt-get update -qq

# Install COLMAP dependencies
echo ""
echo "3️⃣ Installing COLMAP dependencies..."
apt-get install -y -qq \
    git \
    cmake \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
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
    ffmpeg

echo "✅ Dependencies installed"

# Install COLMAP
echo ""
echo "4️⃣ Installing COLMAP..."
if command -v colmap &> /dev/null; then
    echo "✅ COLMAP already installed: $(colmap --version)"
else
    cd /tmp
    rm -rf colmap
    git clone https://github.com/colmap/colmap.git
    cd colmap
    mkdir build && cd build
    cmake .. -DCMAKE_CUDA_ARCHITECTURES=native
    make -j$(nproc)
    make install
    echo "✅ COLMAP installed: $(colmap --version)"
fi

# Clone repository
echo ""
echo "5️⃣ Cloning repository..."
cd /workspace
if [ -d "colmap-mvp" ]; then
    echo "Repository exists, pulling latest..."
    cd colmap-mvp
    git fetch origin
    git reset --hard origin/main
else
    git clone https://github.com/marco-interact/colmap-mvp.git
    cd colmap-mvp
fi

# Setup Python environment
echo ""
echo "6️⃣ Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Initialize database
echo ""
echo "7️⃣ Initializing database..."
python3 << EOF
from main import init_database, create_demo_data
init_database()
result = create_demo_data()
print(f"Demo data: {result}")
EOF

# Start backend
echo ""
echo "8️⃣ Starting backend..."
pkill -f "python.*main.py" || true
nohup python main.py > backend.log 2>&1 &
sleep 8

# Verify backend
echo ""
echo "9️⃣ Verifying backend..."
curl -s http://localhost:8000/health | jq '.'
echo ""
curl -s http://localhost:8000/api/projects | jq '.projects | length'

# Setup Cloudflare tunnel
echo ""
echo "🔟 Setting up Cloudflare tunnel..."
pkill -f cloudflared || true

# Install cloudflared if needed
if ! command -v cloudflared &> /dev/null; then
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -O /tmp/cloudflared.deb
    apt-get install -y /tmp/cloudflared.deb
fi

nohup cloudflared tunnel --url http://localhost:8000 --protocol quic > /tmp/cloudflared.log 2>&1 &
sleep 10

TUNNEL_URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -1)

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "Pod ID: 0pgs4gpmkmkn5y"
echo "SSH: ssh root@203.57.40.175 -p 10123"
echo "Backend: http://localhost:8000"
echo "Tunnel: $TUNNEL_URL"
echo ""
echo "📋 Next: Update Vercel NEXT_PUBLIC_API_URL with tunnel URL"
echo "=================================================="

