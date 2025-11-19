#!/bin/bash
# Robust backend startup script with error handling

set -e  # Exit on error

echo "=========================================="
echo "Metroa Backend Starting..."
echo "=========================================="
echo ""

# Environment check
echo "=== Environment Check ==="
echo "Python version: $(python3 --version)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo ""

# Verify COLMAP
echo "=== COLMAP Check ==="
if command -v colmap &> /dev/null; then
    echo "✅ COLMAP found: $(which colmap)"
    colmap help | head -3
else
    echo "❌ COLMAP not found in PATH"
    exit 1
fi
echo ""

# Verify Python packages
echo "=== Python Package Check ==="
python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" || { echo "❌ FastAPI missing"; exit 1; }
python3 -c "import uvicorn; print('✅ Uvicorn:', uvicorn.__version__)" || { echo "❌ Uvicorn missing"; exit 1; }
python3 -c "import sqlite3; print('✅ SQLite3: OK')" || { echo "❌ SQLite3 missing"; exit 1; }

# Check Open3D (optional)
python3 -c "import open3d; print('✅ Open3D:', open3d.__version__)" 2>/dev/null || echo "⚠️  Open3D not available (optional)"
echo ""

# Verify main.py exists
echo "=== Application Check ==="
if [ -f "main.py" ]; then
    echo "✅ main.py found"
    echo "Size: $(du -h main.py | cut -f1)"
else
    echo "❌ main.py not found"
    exit 1
fi
echo ""

# Create data directories
echo "=== Setting up directories ==="
mkdir -p /workspace/data/results /workspace/data/uploads /workspace/data/cache
mkdir -p /app/data/results /app/data/uploads /app/data/cache
mkdir -p /app/logs
echo "✅ Directories created"
echo ""

# Initialize database
echo "=== Database Check ==="
if [ ! -f "metroa.db" ]; then
    echo "Creating database..."
    python3 -c "import database; database.init_db()" || echo "⚠️  Database init failed (will auto-create on first request)"
fi
echo ""

# Start virtual display for headless OpenGL (COLMAP requirement)
echo "=== Starting Virtual Display ==="
if ! pgrep Xvfb > /dev/null; then
    echo "Starting Xvfb for headless OpenGL..."
    Xvfb :99 -screen 0 1024x768x24 +extension GLX +render -noreset > /dev/null 2>&1 &
    XVFB_PID=$!
    export DISPLAY=:99
    sleep 3
    
    # Verify Xvfb is actually running
    if kill -0 $XVFB_PID 2>/dev/null; then
        echo "✅ Xvfb started on DISPLAY :99 (PID: $XVFB_PID)"
        # Test if X server is responding
        if command -v xdpyinfo &> /dev/null; then
            xdpyinfo -display :99 > /dev/null 2>&1 && echo "✅ X server :99 is responsive" || echo "⚠️  X server not responding yet"
        fi
    else
        echo "❌ Xvfb failed to start!"
        exit 1
    fi
else
    export DISPLAY=:99
    echo "✅ Xvfb already running on DISPLAY :99"
fi
echo ""

# Start the backend
echo "=========================================="
echo "🚀 Starting FastAPI Backend on port 8888"
echo "=========================================="
echo ""

# Run uvicorn WITHOUT exec so we can see errors
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --log-level info \
    --no-access-log 2>&1 || {
    echo ""
    echo "=========================================="
    echo "❌ BACKEND CRASHED!"
    echo "=========================================="
    echo "Exit code: $?"
    echo ""
    echo "Keeping container alive for debugging..."
    tail -f /dev/null
}

