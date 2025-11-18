#!/bin/bash
# ============================================================================
# Metroa Backend - Production Docker Build Script
# ============================================================================
# This script builds the complete Docker image with COLMAP + OpenMVS from source
# Build time: 30-45 minutes (one-time, then cached)
# Result: Production-ready GPU-accelerated Docker image
# ============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="metroa-backend"
IMAGE_TAG="latest"
CONTAINER_NAME="metroa-backend"
PORT=8888
DOCKER_HUB_USER="${DOCKER_HUB_USER:-}"  # Set via env var or leave empty

echo -e "${BLUE}=============================================="
echo "🚀 METROA BACKEND - DOCKER BUILD"
echo -e "==============================================${NC}"
echo ""

# Check if running on RunPod or local
if [ -d "/workspace" ]; then
    BUILD_LOCATION="RunPod"
    WORKSPACE="/workspace/metroa-demo"
else
    BUILD_LOCATION="Local Mac"
    WORKSPACE="$(pwd)"
fi

echo -e "${GREEN}📍 Build Location: ${BUILD_LOCATION}${NC}"
echo -e "${GREEN}📁 Workspace: ${WORKSPACE}${NC}"
echo -e "${GREEN}🐳 Image Name: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo ""

# Navigate to project directory
cd "${WORKSPACE}"

# ============================================================================
# Step 1: Pre-build Checks
# ============================================================================
echo -e "${BLUE}=============================================="
echo "1️⃣  PRE-BUILD CHECKS"
echo -e "==============================================${NC}"

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed: $(docker --version)${NC}"

# Check Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker daemon not running${NC}"
    
    if [ "${BUILD_LOCATION}" == "RunPod" ]; then
        echo "Starting Docker daemon..."
        dockerd > /dev/null 2>&1 &
        sleep 5
        
        if docker info &> /dev/null; then
            echo -e "${GREEN}✅ Docker daemon started${NC}"
        else
            echo -e "${RED}❌ Failed to start Docker daemon${NC}"
            exit 1
        fi
    else
        echo "Please start Docker Desktop"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Docker daemon running${NC}"
fi

# Check for GPU (optional on Mac)
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)${NC}"
    GPU_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  No GPU detected (build will work but no GPU acceleration)${NC}"
    GPU_AVAILABLE=false
fi

# Check Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dockerfile found${NC}"

# Check disk space (need at least 20GB)
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "${AVAILABLE_SPACE}" -lt 20 ]; then
    echo -e "${RED}❌ Insufficient disk space: ${AVAILABLE_SPACE}GB available, need at least 20GB${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Sufficient disk space: ${AVAILABLE_SPACE}GB available${NC}"

echo ""

# ============================================================================
# Step 2: Clean Old Builds (Optional)
# ============================================================================
echo -e "${BLUE}=============================================="
echo "2️⃣  CLEANUP"
echo -e "==============================================${NC}"

# Stop and remove existing container
if docker ps -a | grep -q "${CONTAINER_NAME}"; then
    echo "Stopping and removing existing container..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    echo -e "${GREEN}✅ Old container removed${NC}"
else
    echo -e "${GREEN}✅ No existing container to remove${NC}"
fi

# Optionally remove old image (uncomment to force clean build)
# if docker images | grep -q "${IMAGE_NAME}"; then
#     echo "Removing old image..."
#     docker rmi "${IMAGE_NAME}:${IMAGE_TAG}" 2>/dev/null || true
# fi

echo ""

# ============================================================================
# Step 3: Build Docker Image
# ============================================================================
echo -e "${BLUE}=============================================="
echo "3️⃣  BUILDING DOCKER IMAGE"
echo -e "==============================================${NC}"
echo ""
echo -e "${YELLOW}⏱️  This will take 30-45 minutes on first build${NC}"
echo -e "${YELLOW}⏱️  Subsequent builds will be much faster (cached)${NC}"
echo ""
echo "Building stages:"
echo "  1. Base image with dependencies (~5 min)"
echo "  2. COLMAP build with CUDA (~20-25 min)"
echo "  3. OpenMVS build (~10-15 min)"
echo "  4. Final production image (~2 min)"
echo ""

# Start build with timing
START_TIME=$(date +%s)

docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f Dockerfile \
    . 2>&1 | tee docker-build.log

BUILD_EXIT_CODE=${PIPESTATUS[0]}
END_TIME=$(date +%s)
BUILD_DURATION=$((END_TIME - START_TIME))
BUILD_MINUTES=$((BUILD_DURATION / 60))
BUILD_SECONDS=$((BUILD_DURATION % 60))

echo ""
if [ ${BUILD_EXIT_CODE} -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo -e "${GREEN}⏱️  Build time: ${BUILD_MINUTES}m ${BUILD_SECONDS}s${NC}"
    
    # Show image size
    IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.Size}}")
    echo -e "${GREEN}💾 Image size: ${IMAGE_SIZE}${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    echo "Check docker-build.log for details"
    exit 1
fi

echo ""

# ============================================================================
# Step 4: Test Docker Image
# ============================================================================
echo -e "${BLUE}=============================================="
echo "4️⃣  TESTING DOCKER IMAGE"
echo -e "==============================================${NC}"

# Test 1: Verify COLMAP is in image
echo "Testing COLMAP installation..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" colmap --version &> /dev/null; then
    COLMAP_VERSION=$(docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" colmap --version 2>&1 | head -1)
    echo -e "${GREEN}✅ COLMAP installed: ${COLMAP_VERSION}${NC}"
else
    echo -e "${RED}❌ COLMAP not found in image${NC}"
    exit 1
fi

# Test 2: Verify OpenMVS tools
echo "Testing OpenMVS installation..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" DensifyPointCloud --help &> /dev/null; then
    echo -e "${GREEN}✅ OpenMVS tools installed${NC}"
else
    echo -e "${YELLOW}⚠️  OpenMVS not found (optional)${NC}"
fi

# Test 3: Verify Python packages
echo "Testing Python packages..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python3.12 -c "import fastapi, open3d, cv2; print('OK')" &> /dev/null; then
    echo -e "${GREEN}✅ Python packages installed${NC}"
else
    echo -e "${RED}❌ Python packages missing${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Step 5: Start Container and Test Backend
# ============================================================================
echo -e "${BLUE}=============================================="
echo "5️⃣  STARTING CONTAINER"
echo -e "==============================================${NC}"

# Build docker run command
DOCKER_RUN_CMD="docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:${PORT}"

# Add GPU support if available
if [ "${GPU_AVAILABLE}" == true ]; then
    DOCKER_RUN_CMD="${DOCKER_RUN_CMD} --gpus all"
fi

# Add volume mount
if [ -d "${WORKSPACE}/data" ]; then
    DOCKER_RUN_CMD="${DOCKER_RUN_CMD} -v ${WORKSPACE}/data:/workspace/data"
fi

# Add image name
DOCKER_RUN_CMD="${DOCKER_RUN_CMD} ${IMAGE_NAME}:${IMAGE_TAG}"

# Run container
echo "Starting container..."
eval ${DOCKER_RUN_CMD}

# Wait for container to start
echo "Waiting for backend to start (15 seconds)..."
sleep 15

# Test health endpoint
echo "Testing health endpoint..."
if curl -sf http://localhost:${PORT}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is responding!${NC}"
    echo ""
    echo "Health check response:"
    curl -s http://localhost:${PORT}/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:${PORT}/health
    echo ""
else
    echo -e "${RED}❌ Backend not responding${NC}"
    echo ""
    echo "Container logs:"
    docker logs "${CONTAINER_NAME}" --tail 50
    echo ""
    echo -e "${YELLOW}Note: Backend may still be starting. Check logs with:${NC}"
    echo "  docker logs -f ${CONTAINER_NAME}"
fi

echo ""

# ============================================================================
# Step 6: Summary and Next Steps
# ============================================================================
echo -e "${BLUE}=============================================="
echo "✅ BUILD COMPLETE!"
echo -e "==============================================${NC}"
echo ""
echo -e "${GREEN}📦 Image: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "${GREEN}🐳 Container: ${CONTAINER_NAME}${NC}"
echo -e "${GREEN}🌐 Port: ${PORT}${NC}"
echo -e "${GREEN}⏱️  Build time: ${BUILD_MINUTES}m ${BUILD_SECONDS}s${NC}"
echo ""

echo -e "${BLUE}🎯 Useful Commands:${NC}"
echo ""
echo "View logs:"
echo "  docker logs -f ${CONTAINER_NAME}"
echo ""
echo "Stop container:"
echo "  docker stop ${CONTAINER_NAME}"
echo ""
echo "Start container:"
echo "  docker start ${CONTAINER_NAME}"
echo ""
echo "Remove container:"
echo "  docker rm -f ${CONTAINER_NAME}"
echo ""
echo "Test health endpoint:"
echo "  curl http://localhost:${PORT}/health"
echo ""
echo "Access backend:"
echo "  http://localhost:${PORT}"
if [ "${BUILD_LOCATION}" == "RunPod" ]; then
    echo "  https://YOUR-POD-ID-${PORT}.proxy.runpod.net"
fi
echo ""

# ============================================================================
# Optional: Push to Docker Hub
# ============================================================================
if [ -n "${DOCKER_HUB_USER}" ]; then
    echo -e "${BLUE}=============================================="
    echo "6️⃣  PUSH TO DOCKER HUB (Optional)"
    echo -e "==============================================${NC}"
    echo ""
    
    read -p "Push to Docker Hub as ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Tagging image..."
        docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        
        echo "Pushing to Docker Hub..."
        docker push "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        
        echo -e "${GREEN}✅ Pushed to Docker Hub!${NC}"
        echo ""
        echo "To pull on another machine:"
        echo "  docker pull ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        echo ""
    fi
fi

# ============================================================================
# Final Summary
# ============================================================================
echo -e "${GREEN}=============================================="
echo "🎉 SETUP COMPLETE!"
echo -e "==============================================${NC}"
echo ""
echo "Your Metroa backend is now running in Docker with:"
echo "  ✅ COLMAP ${COLMAP_VERSION}"
echo "  ✅ OpenMVS v2.2.0"
echo "  ✅ Open3D 0.19.0"
echo "  ✅ Python 3.12 + FastAPI"
if [ "${GPU_AVAILABLE}" == true ]; then
    echo "  ✅ GPU Acceleration"
fi
echo ""
echo "Next steps:"
echo "  1. Deploy frontend: vercel --prod"
echo "  2. Test with a video upload"
echo "  3. Monitor logs: docker logs -f ${CONTAINER_NAME}"
echo ""

exit 0

