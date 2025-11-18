#!/bin/bash
# ============================================================================
# Build Metroa Docker Container on RunPod
# ============================================================================
# This script builds the full production Docker image with:
# - COLMAP 3.10 (GPU-accelerated, built from source)
# - OpenMVS v2.2.0 (for ultra-dense point clouds)
# - Open3D 0.19.0 (Python bindings)
# - All Python dependencies
#
# Build time: 30-45 minutes (one-time setup)
# Image size: ~8-12 GB
# ============================================================================

set -e  # Exit on any error

echo "============================================================================"
echo "🐳 METROA DOCKER BUILD SCRIPT FOR RUNPOD"
echo "============================================================================"
echo ""
echo "⏱️  Expected time: 30-45 minutes"
echo "💾 Expected size: 8-12 GB"
echo ""

# Navigate to project directory
cd /workspace/metroa-demo || {
    echo "❌ Error: /workspace/metroa-demo not found"
    echo "Run this script from RunPod terminal"
    exit 1
}

# ============================================================================
# STEP 1: Prerequisites Check
# ============================================================================
echo "============================================================================"
echo "📋 Step 1: Checking Prerequisites"
echo "============================================================================"
echo ""

# Check disk space
echo "💾 Checking disk space..."
AVAILABLE_GB=$(df /workspace | tail -1 | awk '{print int($4/1024/1024)}')
echo "Available space: ${AVAILABLE_GB} GB"
if [ "$AVAILABLE_GB" -lt 20 ]; then
    echo "⚠️  WARNING: Less than 20 GB available. Build may fail."
    echo "Consider cleaning up: docker system prune -a"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Sufficient disk space"
fi
echo ""

# Check GPU
echo "🎮 Checking GPU..."
if nvidia-smi > /dev/null 2>&1; then
    echo "✅ GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
else
    echo "⚠️  No GPU detected. Build will work but COLMAP won't be GPU-accelerated."
fi
echo ""

# Check Docker daemon
echo "🐳 Checking Docker daemon..."
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker daemon not running. Starting it..."
    # Kill any existing dockerd
    pkill dockerd 2>/dev/null || true
    sleep 2
    # Start Docker daemon
    dockerd > /var/log/dockerd.log 2>&1 &
    sleep 5
    
    # Verify it started
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker daemon started"
    else
        echo "❌ Failed to start Docker daemon"
        echo "Check logs: cat /var/log/dockerd.log"
        exit 1
    fi
else
    echo "✅ Docker daemon running"
fi
echo ""

# Check Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found in $(pwd)"
    exit 1
fi
echo "✅ Dockerfile found"
echo ""

# ============================================================================
# STEP 2: Cleanup Old Containers/Images
# ============================================================================
echo "============================================================================"
echo "🧹 Step 2: Cleaning Up Old Containers/Images"
echo "============================================================================"
echo ""

# Stop and remove old metroa containers
echo "Stopping old containers..."
docker ps -a --filter "name=metroa" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true
docker ps -a --filter "name=metroa" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true
echo "✅ Old containers removed"
echo ""

# Ask about removing old images
OLD_IMAGES=$(docker images --filter "reference=metroa-backend" -q)
if [ -n "$OLD_IMAGES" ]; then
    echo "Found old metroa-backend images"
    read -p "Remove old images to save space? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi $OLD_IMAGES 2>/dev/null || true
        echo "✅ Old images removed"
    else
        echo "⏭️  Keeping old images"
    fi
fi
echo ""

# ============================================================================
# STEP 3: Build Docker Image
# ============================================================================
echo "============================================================================"
echo "🔨 Step 3: Building Docker Image"
echo "============================================================================"
echo ""
echo "This will take 30-45 minutes. Progress will be shown below."
echo "The build includes:"
echo "  - COLMAP 3.10 (GPU-enabled, from source)"
echo "  - OpenMVS v2.2.0 (dense reconstruction)"
echo "  - Open3D 0.19.0 (point cloud processing)"
echo "  - Python 3.12 + FastAPI"
echo ""
echo "☕ Good time for a coffee break!"
echo ""
sleep 3

# Build with progress output
BUILD_START=$(date +%s)

docker build \
    --progress=plain \
    --tag metroa-backend:latest \
    --tag metroa-backend:$(date +%Y%m%d) \
    --file Dockerfile \
    . 2>&1 | tee docker-build.log

BUILD_END=$(date +%s)
BUILD_TIME=$((BUILD_END - BUILD_START))
BUILD_MINUTES=$((BUILD_TIME / 60))

echo ""
echo "============================================================================"
echo "✅ Docker Build Complete!"
echo "============================================================================"
echo ""
echo "Build time: ${BUILD_MINUTES} minutes"
echo "Log saved to: docker-build.log"
echo ""

# ============================================================================
# STEP 4: Verify Build
# ============================================================================
echo "============================================================================"
echo "🧪 Step 4: Verifying Build"
echo "============================================================================"
echo ""

# Check image exists
if docker images | grep -q "metroa-backend"; then
    echo "✅ Docker image created successfully"
    echo ""
    echo "Image details:"
    docker images metroa-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
else
    echo "❌ Docker image not found"
    echo "Check build log: cat docker-build.log"
    exit 1
fi
echo ""

# Test image by running verification commands
echo "🔍 Testing image contents..."
echo ""

# Test COLMAP
echo "Testing COLMAP..."
if docker run --rm metroa-backend:latest colmap --version > /dev/null 2>&1; then
    COLMAP_VERSION=$(docker run --rm metroa-backend:latest colmap --version 2>&1 | head -1)
    echo "✅ COLMAP: $COLMAP_VERSION"
else
    echo "⚠️  COLMAP test failed"
fi

# Test OpenMVS
echo "Testing OpenMVS..."
if docker run --rm metroa-backend:latest DensifyPointCloud --help > /dev/null 2>&1; then
    echo "✅ OpenMVS: DensifyPointCloud available"
else
    echo "⚠️  OpenMVS test failed"
fi

# Test Python packages
echo "Testing Python packages..."
if docker run --rm metroa-backend:latest python3.12 -c "import fastapi, open3d, cv2; print('OK')" > /dev/null 2>&1; then
    echo "✅ Python packages: FastAPI, Open3D, OpenCV installed"
else
    echo "⚠️  Python packages test failed"
fi

echo ""

# ============================================================================
# STEP 5: Test Run Container
# ============================================================================
echo "============================================================================"
echo "🚀 Step 5: Test Running Container"
echo "============================================================================"
echo ""

# Clean up any existing test container
docker rm -f metroa-test 2>/dev/null || true

# Run test container
echo "Starting test container..."
docker run -d \
    --name metroa-test \
    --gpus all \
    -p 8889:8888 \
    metroa-backend:latest

echo "Waiting for backend to start (15 seconds)..."
sleep 15

# Test health endpoint
echo "Testing health endpoint..."
if curl -s http://localhost:8889/health > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
    echo ""
    echo "Health check response:"
    curl -s http://localhost:8889/health | python3 -m json.tool
    echo ""
else
    echo "⚠️  Backend not responding. Checking logs..."
    docker logs metroa-test --tail 50
fi

# Stop test container
echo ""
echo "Stopping test container..."
docker stop metroa-test > /dev/null 2>&1
docker rm metroa-test > /dev/null 2>&1
echo "✅ Test complete"
echo ""

# ============================================================================
# SUCCESS! Provide Next Steps
# ============================================================================
echo "============================================================================"
echo "🎉 BUILD COMPLETE! Docker image ready for production use"
echo "============================================================================"
echo ""
echo "📊 Image Info:"
docker images metroa-backend:latest --format "  Size: {{.Size}}\n  Created: {{.CreatedAt}}"
echo ""
echo "🚀 To start the production backend:"
echo ""
echo "  docker run -d \\"
echo "    --name metroa-backend \\"
echo "    --gpus all \\"
echo "    --restart unless-stopped \\"
echo "    -p 8888:8888 \\"
echo "    -v /workspace/metroa-demo/data:/workspace/data \\"
echo "    metroa-backend:latest"
echo ""
echo "🧪 To test the backend:"
echo ""
echo "  curl http://localhost:8888/health"
echo ""
echo "📋 Useful Docker commands:"
echo ""
echo "  View logs:       docker logs -f metroa-backend"
echo "  Stop container:  docker stop metroa-backend"
echo "  Start container: docker start metroa-backend"
echo "  Remove container: docker rm -f metroa-backend"
echo "  Shell access:    docker exec -it metroa-backend bash"
echo ""
echo "💾 To save the image (optional):"
echo ""
echo "  # Save to file"
echo "  docker save metroa-backend:latest | gzip > metroa-backend.tar.gz"
echo ""
echo "  # Push to Docker Hub (requires login)"
echo "  docker tag metroa-backend:latest yourusername/metroa-backend:latest"
echo "  docker push yourusername/metroa-backend:latest"
echo ""
echo "============================================================================"
echo "Build log saved to: docker-build.log"
echo "Total build time: ${BUILD_MINUTES} minutes"
echo "============================================================================"
echo ""

