#!/bin/bash
################################################################################
# COLMAP Backend Persistent Startup Script
# Simple, reliable, no systemd/supervisor needed
################################################################################

echo "🚀 Starting COLMAP Backend (Persistent Mode)..."

# Kill any existing processes
killall -9 python3 uvicorn Xvfb 2>/dev/null || true
sleep 2

# Start Xvfb in background
echo "Starting Xvfb..."
nohup Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /workspace/xvfb.log 2>&1 &
sleep 2

# Verify Xvfb started
if pgrep Xvfb > /dev/null; then
    echo "✅ Xvfb running (PID: $(pgrep Xvfb))"
else
    echo "❌ Xvfb failed to start"
    exit 1
fi

# Start COLMAP backend
echo "Starting COLMAP backend..."
cd /workspace/colmap-demo
source venv/bin/activate

export DISPLAY=:99
export QT_QPA_PLATFORM=offscreen
export MESA_GL_VERSION_OVERRIDE=3.3
export CUDA_VISIBLE_DEVICES=0
export STORAGE_DIR=/workspace/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/data/cache
export UPLOADS_DIR=/workspace/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/server.log 2>&1 &
BACKEND_PID=$!

sleep 5

# Verify backend started
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ Backend running (PID: $BACKEND_PID)"
else
    echo "⚠️  Backend may have crashed. Checking..."
    if pgrep -f "uvicorn main:app" > /dev/null; then
        echo "✅ Backend is running (found via pgrep)"
    else
        echo "❌ Backend not running. Check logs:"
        echo "tail -f /workspace/server.log"
        exit 1
    fi
fi

# Test health
echo ""
echo "Testing health endpoint..."
sleep 2
HEALTH=$(curl -s http://localhost:8000/health)
if [ ! -z "$HEALTH" ]; then
    echo "✅ Backend is healthy!"
    echo "$HEALTH"
else
    echo "⚠️  Backend not responding yet. Wait a few seconds and try:"
    echo "curl http://localhost:8000/health"
fi

echo ""
echo "=========================================="
echo "✨ COLMAP Backend Running!"
echo "=========================================="
echo ""
echo "📊 Status:"
echo "  • Xvfb PID: $(pgrep Xvfb)"
echo "  • Backend PID: $(pgrep -f 'uvicorn main:app')"
echo "  • Local: http://localhost:8000/health"
echo "  • Public: https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health"
echo ""
echo "📝 Logs:"
echo "  • Backend: tail -f /workspace/server.log"
echo "  • Xvfb: tail -f /workspace/xvfb.log"
echo ""
echo "🔄 Restart: /workspace/start-colmap-persistent.sh"
echo ""
echo "💡 Processes are running in background with nohup"
echo "   They will survive terminal closure!"
echo ""





