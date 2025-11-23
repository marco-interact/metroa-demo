#!/bin/bash
# ============================================================================
# Build Metroa Docker Image Locally (Mac/Linux with Docker Desktop)
# ============================================================================
# This script builds the Docker image on your local machine
# Requires: Docker Desktop installed and running
# ============================================================================

set -e

echo "============================================================================"
echo "🐳 BUILDING METROA DOCKER IMAGE LOCALLY"
echo "============================================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo ""
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Choose build type
echo "Choose build type:"
echo ""
echo "1) FAST BUILD (Recommended) - 5-10 minutes"
echo "   Uses pre-compiled COLMAP from Ubuntu"
echo ""
echo "2) PRODUCTION BUILD - 30-45 minutes"
echo "   Compiles COLMAP from source for maximum performance"
echo ""

read -p "Select (1 or 2): " BUILD_TYPE

case "$BUILD_TYPE" in
    1)
        DOCKERFILE="Dockerfile.fast"
        TAG="metroa-backend:fast"
        BUILD_TIME="5-10 minutes"
        ;;
    2)
        DOCKERFILE="Dockerfile"
        TAG="metroa-backend:latest"
        BUILD_TIME="30-45 minutes"
        ;;
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "Building with $DOCKERFILE"
echo "Platform: linux/amd64 (RunPod compatible)"
echo "Expected time: $BUILD_TIME"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Build cancelled"
    exit 0
fi

# Build the image
echo ""
echo "============================================================================"
echo "🔨 BUILDING DOCKER IMAGE"
echo "============================================================================"
echo ""

BUILD_START=$(date +%s)

docker build \
    --platform=linux/amd64 \
    -f $DOCKERFILE \
    -t $TAG \
    --progress=plain \
    . 2>&1 | tee docker-build.log

BUILD_END=$(date +%s)
BUILD_MINUTES=$(( (BUILD_END - BUILD_START) / 60 ))

echo ""
echo "============================================================================"
echo "✅ BUILD COMPLETE!"
echo "============================================================================"
echo ""
echo "Build time: $BUILD_MINUTES minutes"
echo "Image tag: $TAG"
echo ""

# Show image info
docker images $TAG

echo ""
echo "============================================================================"
echo "🧪 TESTING IMAGE"
echo "============================================================================"
echo ""

# Test the image
echo "Starting test container..."
docker run -d --name metroa-test -p 8889:8888 $TAG

echo "Waiting for backend to start..."
sleep 15

# Test health endpoint
if curl -s http://localhost:8889/health > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
    echo ""
    curl -s http://localhost:8889/health | python3 -m json.tool
    echo ""
else
    echo "⚠️  Backend not responding. Check logs:"
    docker logs metroa-test --tail 20
fi

# Cleanup test container
docker stop metroa-test > /dev/null 2>&1
docker rm metroa-test > /dev/null 2>&1

echo ""
echo "============================================================================"
echo "📦 NEXT STEPS"
echo "============================================================================"
echo ""
echo "1️⃣  Test locally:"
echo "  docker run -d --name metroa-backend -p 8888:8888 \\"
echo "    -v \$(pwd)/data:/workspace/data $TAG"
echo "  curl http://localhost:8888/health"
echo ""
echo "2️⃣  Push to Docker Hub:"
echo "  docker login"
echo "  docker tag $TAG YOUR_USERNAME/metroa-backend:latest"
echo "  docker push YOUR_USERNAME/metroa-backend:latest"
echo ""
echo "3️⃣  Use in RunPod:"
echo "  Container Image: YOUR_USERNAME/metroa-backend:latest"
echo "  Expose Ports: 8888"
echo ""
echo "============================================================================"

