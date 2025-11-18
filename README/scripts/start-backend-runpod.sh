#!/bin/bash
# ============================================================================
# Start Metroa Backend on RunPod (Direct - No Docker)
# ============================================================================

set -e

cd /workspace/metroa-demo

echo "============================================================================"
echo "🚀 STARTING METROA BACKEND"
echo "============================================================================"
echo ""

# Kill any existing backend
echo "🧹 Cleaning up old processes..."
pkill -f "python.*main.py" 2>/dev/null || true
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Cleanup complete"
echo ""

# Start in screen session (persistent)
echo "🚀 Starting backend in screen session..."
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py 2>&1 | tee logs/backend.log"
echo "✅ Backend started in screen session 'metroa-backend'"
echo ""

# Wait for startup
echo "⏳ Waiting for backend to start (10 seconds)..."
sleep 10

# Test health
echo "🧪 Testing backend health..."
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo ""
    echo "============================================================================"
    echo "✅ BACKEND IS RUNNING!"
    echo "============================================================================"
    echo ""
    echo "Health check response:"
    curl -s http://localhost:8888/health | python -m json.tool 2>/dev/null || curl -s http://localhost:8888/health
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:        tail -f logs/backend.log"
    echo "  Reconnect screen: screen -r metroa-backend"
    echo "  List screens:     screen -ls"
    echo "  Stop backend:     pkill -f 'python.*main.py'"
    echo ""
    echo "🌐 Access URLs:"
    echo "  Local:        http://localhost:8888"
    echo "  Health:       http://localhost:8888/health"
    echo "  API Docs:     http://localhost:8888/docs"
    echo "  RunPod Proxy: https://$(hostname)-8888.proxy.runpod.net"
    echo ""
else
    echo ""
    echo "⚠️  Backend not responding yet"
    echo ""
    echo "Check logs:"
    tail -20 logs/backend.log
    echo ""
    echo "Try manual start:"
    echo "  python main.py"
fi

echo "============================================================================"

