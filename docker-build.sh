#!/bin/bash
################################################################################
# Build Metroa Backend GPU Docker Image
# 
# This script builds the production-ready GPU base image containing:
# - COLMAP 3.10 (CUDA-enabled)
# - OpenMVS v2.2.0
# - Open3D 0.19.0
# - Python 3.12 + FastAPI
#
# Usage:
#   ./docker-build.sh [tag] [--push]
#
# Examples:
#   ./docker-build.sh                    # Build with tag 'latest'
#   ./docker-build.sh v1.0.0             # Build with tag 'v1.0.0'
#   ./docker-build.sh v1.0.0 --push      # Build and push to registry
#
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
IMAGE_NAME="metroa-backend"
TAG="${1:-latest}"
DOCKERFILE="Dockerfile"
PUSH_TO_REGISTRY=false

# Check for --push flag
if [[ "$*" == *"--push"* ]]; then
    PUSH_TO_REGISTRY=true
fi

echo "=================================================="
echo "🔨 Building Metroa Backend GPU Image"
echo "=================================================="
echo ""
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Dockerfile: ${DOCKERFILE}"
echo "Push to registry: ${PUSH_TO_REGISTRY}"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Check if NVIDIA runtime is available (for GPU support)
if ! docker info 2>/dev/null | grep -q nvidia; then
    echo -e "${YELLOW}⚠️  NVIDIA Docker runtime not detected${NC}"
    echo -e "${YELLOW}   Image will build but GPU features may not work${NC}"
    echo ""
fi

# Build the image
echo -e "${BLUE}📦 Building Docker image...${NC}"
echo -e "${YELLOW}⏱  This will take 30-45 minutes (COLMAP + OpenMVS builds)${NC}"
echo ""

DOCKER_BUILDKIT=1 docker build \
    --tag ${IMAGE_NAME}:${TAG} \
    --file ${DOCKERFILE} \
    --progress=plain \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    
    # Show image info
    echo "Image details:"
    docker images ${IMAGE_NAME}:${TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    
    # Push if requested
    if [ "$PUSH_TO_REGISTRY" = true ]; then
        echo -e "${BLUE}📤 Pushing image to registry...${NC}"
        docker push ${IMAGE_NAME}:${TAG}
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Image pushed successfully!${NC}"
        else
            echo -e "${RED}❌ Failed to push image${NC}"
            exit 1
        fi
    fi
    
    echo ""
    echo "=================================================="
    echo -e "${GREEN}✨ Build Complete!${NC}"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Test locally (with GPU):"
    echo "   docker run --gpus all -p 8888:8888 ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "2. Test health endpoint:"
    echo "   curl http://localhost:8888/health"
    echo ""
    echo "3. Push to registry (if not already done):"
    echo "   docker push ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "4. Use in RunPod:"
    echo "   Update RunPod template to use: ${IMAGE_NAME}:${TAG}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

