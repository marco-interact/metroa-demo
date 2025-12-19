#!/bin/bash
# ============================================================================
# Metroa Backend Deployment Script (BYOC)
# ============================================================================
# 
# This script handles the full lifecycle of deploying the custom COLMAP backend
# to RunPod using the "Bring Your Own Container" workflow.
#
# Steps:
# 1. Build Docker image locally (optimized for RunPod)
# 2. Push image to Docker Hub
# 3. Provide instructions for deploying on RunPod
#
# Usage: ./deploy.sh
# Example: ./deploy.sh
# ============================================================================

# Configuration
IMAGE_NAME="macoaurelio/metroa-backend"
TAG="latest"
FULL_IMAGE="$IMAGE_NAME:$TAG"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   Metroa Backend Deployment (LATEST ONLY)            ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# ----------------------------------------------------------------------------
# 0. Clean Local Versions (Optional)
# ----------------------------------------------------------------------------
echo -e "${YELLOW}[0/3] Cleaning up old local versions...${NC}"
# Remove dangling images and previous builds of this image to ensure freshness
docker rmi "$FULL_IMAGE" 2>/dev/null || true
echo "Local cleanup complete."
echo ""

# ----------------------------------------------------------------------------
# 1. Build Docker Image
# ----------------------------------------------------------------------------
echo -e "${YELLOW}[1/3] Building Docker Image ($FULL_IMAGE)...${NC}"
echo "Using Dockerfile (Optimized for Production)..."

# Build for linux/amd64 (Required for RunPod)
# Use buildx for proper cross-platform builds and direct push capability
# This ensures AMD64 architecture compatibility with RunPod infrastructure
docker buildx build --platform linux/amd64 --progress=plain -t "$FULL_IMAGE" --load -f Dockerfile .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the error log above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# ----------------------------------------------------------------------------
# 2. Push to Docker Hub
# ----------------------------------------------------------------------------
echo -e "${YELLOW}[2/3] Pushing to Docker Hub...${NC}"

# Check if logged in - simplified check
echo "Checking Docker Hub login..."
docker info > /dev/null 2>&1

echo "Pushing $FULL_IMAGE..."
docker push "$FULL_IMAGE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Push failed!${NC}"
    echo "Common fixes:"
    echo "1. Run 'docker login' and check credentials"
    echo "2. Ensure repository '$IMAGE_NAME' exists on Docker Hub"
    exit 1
fi

echo -e "${GREEN}✅ Push successful!${NC}"
echo ""

# ----------------------------------------------------------------------------
# 3. Deployment Instructions
# ----------------------------------------------------------------------------
echo -e "${YELLOW}[3/3] Deployment Instructions${NC}"
echo "--------------------------------------------------------"
echo "Go to RunPod Console: https://www.runpod.io/console/pods"
echo ""
echo "1. Click 'Edit' on your pod"
echo "2. Set Container Image to:"
echo -e "   ${GREEN}$FULL_IMAGE${NC}"
echo "3. Important: If the image name hasn't changed,"
echo "   you MUST stop the pod and start it again to pull the new version."
echo "   (Or check 'Image Pull Policy' if available)"
echo ""
echo "🚀 Pod Restart Required for 'latest' updates!"
echo "--------------------------------------------------------"
echo ""
