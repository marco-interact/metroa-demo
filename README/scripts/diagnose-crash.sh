#!/bin/bash
# Quick diagnostic script to find why backend crashes on RunPod

set +e  # Don't exit on errors

cd /workspace/metroa-demo

echo "=========================================="
echo "🔍 METROA BACKEND CRASH DIAGNOSTIC"
echo "=========================================="
echo ""

# 1. Check Python
echo "=== Python Version ==="
python --version
echo ""

# 2. Check if dependencies are installed
echo "=== Critical Dependencies ==="
python -c "
import sys
packages = ['fastapi', 'uvicorn', 'cv2', 'numpy', 'open3d', 'sqlite3']
for pkg in packages:
    try:
        if pkg == 'cv2':
            __import__('cv2')
            print(f'✅ OpenCV')
        else:
            __import__(pkg)
            print(f'✅ {pkg}')
    except ImportError as e:
        print(f'❌ {pkg} - MISSING')
"
echo ""

# 3. Check COLMAP
echo "=== COLMAP Check ==="
if command -v colmap > /dev/null 2>&1; then
    echo "✅ COLMAP found: $(which colmap)"
    colmap --version 2>&1 | head -1
else
    echo "❌ COLMAP not found - INSTALL REQUIRED"
fi
echo ""

# 4. Check FFmpeg
echo "=== FFmpeg Check ==="
if command -v ffmpeg > /dev/null 2>&1; then
    echo "✅ FFmpeg found"
else
    echo "❌ FFmpeg not found - INSTALL REQUIRED"
fi
echo ""

# 5. Check port 8888
echo "=== Port 8888 Status ==="
if lsof -i:8888 > /dev/null 2>&1; then
    echo "⚠️  Port 8888 is IN USE:"
    lsof -i:8888
else
    echo "✅ Port 8888 is free"
fi
echo ""

# 6. Check data directories
echo "=== Data Directories ==="
for dir in data data/uploads data/results data/cache; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing - CREATING NOW"
        mkdir -p "$dir"
    fi
done
echo ""

# 7. Check disk space
echo "=== Disk Space ==="
df -h /workspace | tail -1
echo ""

# 8. Check memory
echo "=== Memory ==="
free -h | grep "Mem:"
echo ""

# 9. Test actual backend startup
echo "=========================================="
echo "🚀 TESTING BACKEND STARTUP"
echo "=========================================="
echo ""
echo "Starting backend (will show actual error if any)..."
echo "Press Ctrl+C if it hangs"
echo ""

# Run Python directly to see the error
timeout 10 python main.py 2>&1 | tee /tmp/backend_test.log &
BACKEND_PID=$!

sleep 5

# Test if it's responding
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo ""
    echo "✅✅✅ BACKEND IS WORKING! ✅✅✅"
    echo ""
    curl http://localhost:8888/health
    kill $BACKEND_PID 2>/dev/null
else
    echo ""
    echo "❌ BACKEND NOT RESPONDING"
    echo ""
    echo "Last 20 lines of output:"
    tail -20 /tmp/backend_test.log
    kill $BACKEND_PID 2>/dev/null
fi

echo ""
echo "=========================================="
echo "📋 DIAGNOSTIC COMPLETE"
echo "=========================================="
echo ""
echo "If backend is not working, check the error above."
echo ""
echo "Common fixes:"
echo "  1. Missing dependencies: pip install -r requirements.txt"
echo "  2. COLMAP not found: apt-get install -y colmap"
echo "  3. Port in use: lsof -ti:8888 | xargs kill -9"
echo ""
echo "Full troubleshooting guide:"
echo "  cat README/troubleshooting/DIAGNOSE_BACKEND_CRASH.md"
echo ""

