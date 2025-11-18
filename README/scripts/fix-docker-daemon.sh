#!/bin/bash
# Fix Docker Daemon on RunPod
# Solves: "Docker daemon not running" error

set -e

echo "============================================================================"
echo "🔧 FIXING DOCKER DAEMON ON RUNPOD"
echo "============================================================================"
echo ""

# Kill any stuck Docker processes
echo "1️⃣ Killing stuck Docker processes..."
pkill -9 dockerd 2>/dev/null || true
pkill -9 containerd 2>/dev/null || true
pkill -9 docker 2>/dev/null || true
sleep 3
echo "✅ Cleaned up processes"
echo ""

# Clean up Docker socket
echo "2️⃣ Cleaning Docker socket..."
rm -f /var/run/docker.sock
rm -f /var/run/docker.pid
echo "✅ Socket cleaned"
echo ""

# Create necessary directories
echo "3️⃣ Creating Docker directories..."
mkdir -p /var/run
mkdir -p /var/lib/docker
echo "✅ Directories created"
echo ""

# Start Docker daemon with proper configuration
echo "4️⃣ Starting Docker daemon..."
echo ""
echo "This may take 10-15 seconds..."

# Start dockerd in background with logging
nohup dockerd \
    --host=unix:///var/run/docker.sock \
    --storage-driver=overlay2 \
    --data-root=/var/lib/docker \
    > /var/log/dockerd.log 2>&1 &

DOCKERD_PID=$!
echo "Docker daemon started with PID: $DOCKERD_PID"
echo ""

# Wait for Docker to be ready
echo "5️⃣ Waiting for Docker to be ready..."
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker daemon is ready!"
        echo ""
        break
    fi
    sleep 1
    WAITED=$((WAITED + 1))
    echo -ne "  Waiting... ${WAITED}s / ${MAX_WAIT}s\r"
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo ""
    echo "❌ Docker daemon failed to start after ${MAX_WAIT} seconds"
    echo ""
    echo "Check logs:"
    tail -50 /var/log/dockerd.log
    exit 1
fi

# Verify Docker is working
echo "6️⃣ Verifying Docker..."
docker version
echo ""

echo "============================================================================"
echo "✅ DOCKER DAEMON FIXED AND RUNNING!"
echo "============================================================================"
echo ""
echo "You can now run:"
echo "  docker ps"
echo "  docker images"
echo "  bash README/scripts/build-docker-runpod.sh"
echo ""
echo "If Docker stops, run this script again:"
echo "  bash README/scripts/fix-docker-daemon.sh"
echo ""

