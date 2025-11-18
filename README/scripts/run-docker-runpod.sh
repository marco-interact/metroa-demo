#!/bin/bash
# ============================================================================
# Run Metroa Docker Container on RunPod
# ============================================================================
# This script runs the pre-built metroa-backend Docker image
# Use this after building with build-docker-runpod.sh
# ============================================================================

set -e

echo "============================================================================"
echo "🚀 STARTING METROA DOCKER CONTAINER"
echo "============================================================================"
echo ""

cd /workspace/metroa-demo

# ============================================================================
# Check Prerequisites
# ============================================================================
echo "📋 Checking prerequisites..."
echo ""

# Check Docker daemon
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker daemon not running. Starting it..."
    pkill dockerd 2>/dev/null || true
    sleep 2
    dockerd > /var/log/dockerd.log 2>&1 &
    sleep 5
    
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Failed to start Docker daemon"
        exit 1
    fi
    echo "✅ Docker daemon started"
else
    echo "✅ Docker daemon running"
fi
echo ""

# Check if image exists
if ! docker images | grep -q "metroa-backend"; then
    echo "❌ Docker image 'metroa-backend' not found"
    echo ""
    echo "Build the image first:"
    echo "  bash README/scripts/build-docker-runpod.sh"
    exit 1
fi
echo "✅ Docker image found"
echo ""

# ============================================================================
# Cleanup Old Container
# ============================================================================
echo "🧹 Cleaning up old containers..."
if docker ps -a --format "{{.Names}}" | grep -q "^metroa-backend$"; then
    echo "Stopping and removing old metroa-backend container..."
    docker stop metroa-backend 2>/dev/null || true
    docker rm metroa-backend 2>/dev/null || true
    echo "✅ Old container removed"
else
    echo "✅ No old container to remove"
fi
echo ""

# ============================================================================
# Create Data Directories
# ============================================================================
echo "📁 Creating data directories..."
mkdir -p /workspace/metroa-demo/data/{uploads,results,cache}
echo "✅ Data directories ready"
echo ""

# ============================================================================
# Start Container
# ============================================================================
echo "============================================================================"
echo "🐳 Starting Docker Container"
echo "============================================================================"
echo ""

docker run -d \
    --name metroa-backend \
    --gpus all \
    --restart unless-stopped \
    -p 8888:8888 \
    -v /workspace/metroa-demo/data:/workspace/data \
    -e CUDA_VISIBLE_DEVICES=0 \
    metroa-backend:latest

echo "✅ Container started"
echo ""

# ============================================================================
# Wait for Backend to Start
# ============================================================================
echo "⏳ Waiting for backend to start (15 seconds)..."
for i in {15..1}; do
    echo -ne "  $i seconds remaining...\r"
    sleep 1
done
echo ""

# ============================================================================
# Test Health Endpoint
# ============================================================================
echo "============================================================================"
echo "🧪 Testing Backend"
echo "============================================================================"
echo ""

MAX_RETRIES=3
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8888/health > /dev/null 2>&1; then
        echo "✅ Backend is responding!"
        echo ""
        echo "Health check response:"
        curl -s http://localhost:8888/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8888/health
        echo ""
        break
    else
        RETRY=$((RETRY + 1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            echo "⏳ Backend not ready yet, retrying... ($RETRY/$MAX_RETRIES)"
            sleep 5
        else
            echo "⚠️  Backend not responding after $MAX_RETRIES attempts"
            echo ""
            echo "Container logs (last 30 lines):"
            docker logs metroa-backend --tail 30
            echo ""
            echo "Check full logs: docker logs -f metroa-backend"
            exit 1
        fi
    fi
done

# ============================================================================
# Show Container Info
# ============================================================================
echo "============================================================================"
echo "📊 Container Info"
echo "============================================================================"
echo ""
docker ps --filter "name=metroa-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# ============================================================================
# Success! Show Usage Info
# ============================================================================
echo "============================================================================"
echo "✅ BACKEND RUNNING SUCCESSFULLY!"
echo "============================================================================"
echo ""
echo "🌐 Access URLs:"
echo ""
echo "  Local:          http://localhost:8888"
echo "  Health check:   http://localhost:8888/health"
echo "  API docs:       http://localhost:8888/docs"
echo ""

# Try to detect RunPod proxy URL
POD_ID=$(hostname)
if [ -n "$RUNPOD_POD_ID" ]; then
    POD_ID=$RUNPOD_POD_ID
fi
echo "  RunPod Proxy:   https://${POD_ID}-8888.proxy.runpod.net"
echo ""

echo "📋 Useful commands:"
echo ""
echo "  View logs (live):     docker logs -f metroa-backend"
echo "  View logs (last 50):  docker logs metroa-backend --tail 50"
echo "  Check status:         docker ps --filter name=metroa-backend"
echo "  Stop backend:         docker stop metroa-backend"
echo "  Start backend:        docker start metroa-backend"
echo "  Restart backend:      docker restart metroa-backend"
echo "  Remove container:     docker rm -f metroa-backend"
echo "  Shell access:         docker exec -it metroa-backend bash"
echo ""

echo "🔧 Container persists across terminal disconnects (--restart unless-stopped)"
echo ""
echo "============================================================================"

