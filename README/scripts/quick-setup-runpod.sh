#!/bin/bash
# Quick RunPod Setup - Gets backend running in 2 minutes
# Run this: bash README/scripts/quick-setup-runpod.sh

set -e

echo "=========================================="
echo "🚀 METROA QUICK SETUP FOR RUNPOD"
echo "=========================================="
echo ""

cd /workspace/metroa-demo

# 1. Install COLMAP
echo "📦 Installing COLMAP..."
apt-get update -qq
apt-get install -y -qq colmap ffmpeg libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 > /dev/null 2>&1
echo "✅ COLMAP installed"
echo ""

# 2. Verify COLMAP
echo "🔍 Verifying COLMAP..."
if colmap --version > /dev/null 2>&1; then
    echo "✅ COLMAP $(colmap --version 2>&1 | head -1)"
else
    echo "❌ COLMAP installation failed"
    exit 1
fi
echo ""

# 3. Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✅ Python packages installed"
echo ""

# 4. Create directories
echo "📁 Creating data directories..."
mkdir -p data/{uploads,results,cache}
echo "✅ Directories created"
echo ""

# 5. Kill any existing backend
echo "🧹 Cleaning up old processes..."
pkill -f "python.*main.py" 2>/dev/null || true
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Cleanup complete"
echo ""

# 6. Test imports
echo "🧪 Testing imports..."
python -c "
import sys
try:
    from colmap_processor import COLMAPProcessor
    from colmap_binary_parser import COLMAPBinaryParser
    from quality_presets import get_preset
    import fastapi
    import open3d
    import cv2
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
echo ""

# 7. Start backend in screen
echo "🚀 Starting backend in screen session..."
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py 2>&1 | tee backend.log"
echo "✅ Backend started in screen session 'metroa-backend'"
echo ""

# 8. Wait and test
echo "⏳ Waiting for backend to start (10 seconds)..."
sleep 10

echo "🧪 Testing backend health..."
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "✅✅✅ SUCCESS! Backend is running! ✅✅✅"
    echo "=========================================="
    echo ""
    echo "Health check response:"
    curl -s http://localhost:8888/health | python -m json.tool
    echo ""
    echo "📊 Useful commands:"
    echo "  View logs:        tail -f backend.log"
    echo "  Reconnect screen: screen -r metroa-backend"
    echo "  Check status:     curl http://localhost:8888/health"
    echo "  List screens:     screen -ls"
    echo ""
    echo "🌐 Access via RunPod proxy:"
    echo "  https://YOUR-POD-ID-8888.proxy.runpod.net/health"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Backend not responding"
    echo "=========================================="
    echo ""
    echo "Check logs:"
    tail -20 backend.log
    echo ""
    echo "Try manual start:"
    echo "  python main.py"
    echo ""
fi

echo "Setup complete!"

