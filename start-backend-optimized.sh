#!/bin/bash
# Optimized backend startup script for RunPod
# Simplified, robust, with proper error handling

# Simple logging (no complex process substitution)
LOG_FILE="/tmp/backend-startup.log"
exec >> "$LOG_FILE" 2>&1

echo "=========================================="
echo "Metroa Backend Starting..."
echo "=========================================="
echo "Timestamp: $(date)"
echo "Hostname: $(hostname)"
echo ""

# Don't exit on errors - we want to see what fails
set +e

# ============================================================================
# 1. Environment Check
# ============================================================================
echo "=== 1/7 Environment Check ==="
echo "Python: $(python3 --version 2>&1)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "PATH: $PATH"
echo ""

# ============================================================================
# 2. Verify COLMAP
# ============================================================================
echo "=== 2/7 COLMAP Verification ==="
if command -v colmap &> /dev/null; then
    echo "✅ COLMAP found: $(which colmap)"
    colmap help 2>&1 | head -3 || true
else
    echo "❌ FATAL: COLMAP not found"
    echo "Container cannot function without COLMAP"
    sleep infinity  # Keep container alive for debugging
fi
echo ""

# ============================================================================
# 3. Verify Python Dependencies
# ============================================================================
echo "=== 3/7 Python Package Check ==="
python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>&1 || echo "❌ FastAPI MISSING"
python3 -c "import uvicorn; print('✅ Uvicorn:', uvicorn.__version__)" 2>&1 || echo "❌ Uvicorn MISSING"
python3 -c "import open3d; print('✅ Open3D:', open3d.__version__)" 2>&1 || echo "⚠️  Open3D unavailable"
echo ""

# ============================================================================
# 4. Verify Application Code
# ============================================================================
echo "=== 4/7 Application Check ==="
if [ -f "main.py" ]; then
    echo "✅ main.py found ($(du -h main.py | cut -f1))"
else
    echo "❌ FATAL: main.py not found"
    ls -la /app/ | head -20
    sleep infinity
fi
echo ""

# ============================================================================
# 5. Create Directories
# ============================================================================
echo "=== 5/7 Directory Setup ==="
mkdir -p /workspace/data/{results,uploads,cache} 2>/dev/null || true
mkdir -p /app/data/{results,uploads,cache} /app/logs 2>/dev/null || true

# Ensure XDG_RUNTIME_DIR has correct permissions (Qt/COLMAP requirement)
mkdir -p /tmp/runtime-root 2>/dev/null || true
chmod 0700 /tmp/runtime-root 2>/dev/null || true

echo "✅ Directories created"
ls -ld /workspace/data/* /app/data/* 2>/dev/null | head -10 || true
echo "XDG_RUNTIME_DIR permissions: $(stat -c '%a' /tmp/runtime-root 2>/dev/null || echo 'N/A')"
echo ""

# ============================================================================
# 6. Start Xvfb (Virtual Display for OpenGL)
# ============================================================================
echo "=== 6/7 Starting Xvfb ==="
if pgrep -x Xvfb > /dev/null; then
    echo "✅ Xvfb already running"
else
    echo "Starting Xvfb on DISPLAY :99..."
    # Start Xvfb with proper error capture
    Xvfb :99 -screen 0 1024x768x24 +extension GLX +render -noreset >> /tmp/xvfb.log 2>&1 &
    XVFB_PID=$!
    
    # Wait and verify
    sleep 2
    if kill -0 $XVFB_PID 2>/dev/null; then
        echo "✅ Xvfb started (PID: $XVFB_PID)"
    else
        echo "⚠️  Xvfb failed to start (non-fatal)"
        cat /tmp/xvfb.log 2>/dev/null | head -10 || true
    fi
fi

# Export DISPLAY for all child processes
export DISPLAY=:99
echo "DISPLAY=$DISPLAY"
echo ""

# ============================================================================
# 7. Start FastAPI Backend
# ============================================================================
echo "=== 7/7 Starting Backend ==="
echo "=========================================="
echo "🚀 FastAPI Backend on port 8888"
echo "=========================================="
echo ""

# Start backend and capture logs
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --log-level info \
    --no-access-log

# If we get here, backend crashed
EXITCODE=$?
echo ""
echo "=========================================="
echo "❌ BACKEND EXITED (code: $EXITCODE)"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""
echo "Last 50 lines of log:"
tail -50 "$LOG_FILE"
echo ""
echo "Keeping container alive for debugging..."
echo "SSH in and check /tmp/backend-startup.log"
echo ""

# Keep container alive forever
sleep infinity

