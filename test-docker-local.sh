#!/bin/bash
# Local Docker Test Script
# Tests the image before deploying to RunPod

set -e

IMAGE_NAME="macoaurelio/metroa-backend:latest"
CONTAINER_NAME="metroa-test"

echo "========================================"
echo "🧪 Metroa Docker Local Test"
echo "========================================"
echo ""

# Cleanup any existing test container
echo "=== Cleanup ==="
docker rm -f $CONTAINER_NAME 2>/dev/null || true
echo "✅ Cleaned up old containers"
echo ""

# Build the image
echo "=== Building Image ==="
echo "Building: $IMAGE_NAME"
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.optimized \
    -t $IMAGE_NAME \
    . || {
    echo "❌ Build failed!"
    exit 1
}
echo "✅ Build successful"
echo ""

# Get image size
echo "=== Image Info ==="
docker images $IMAGE_NAME --format "Size: {{.Size}}"
echo ""

# Start container
echo "=== Starting Container ==="
docker run -d \
    --name $CONTAINER_NAME \
    --platform=linux/amd64 \
    -p 8888:8888 \
    $IMAGE_NAME || {
    echo "❌ Container start failed!"
    exit 1
}
echo "✅ Container started: $CONTAINER_NAME"
echo ""

# Wait for startup
echo "=== Waiting for Startup (30s) ==="
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo " done!"
echo ""

# Check logs
echo "=== Startup Logs ==="
docker logs $CONTAINER_NAME 2>&1 | tail -50
echo ""

# Check if backend is running
echo "=== Process Check ==="
docker exec $CONTAINER_NAME ps aux | grep -E "(Xvfb|uvicorn|python)" | grep -v grep || echo "⚠️  No processes found"
echo ""

# Test health endpoint
echo "=== Health Check ==="
echo "Testing http://localhost:8888/health ..."
sleep 5  # Extra wait

if curl -f -s http://localhost:8888/health > /tmp/health-response.json; then
    echo "✅ HEALTH CHECK PASSED"
    cat /tmp/health-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/health-response.json
    echo ""
else
    echo "❌ HEALTH CHECK FAILED"
    echo ""
    echo "Container logs:"
    docker logs $CONTAINER_NAME 2>&1 | tail -100
    echo ""
    echo "Container is still running for debugging..."
    echo "To check: docker exec -it $CONTAINER_NAME bash"
    echo "To view logs: docker logs -f $CONTAINER_NAME"
    echo "To stop: docker rm -f $CONTAINER_NAME"
    exit 1
fi

# Test detailed info endpoint
echo "=== Testing /api/system/info ==="
curl -s http://localhost:8888/api/system/info 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "⚠️  Endpoint not available"
echo ""

# Success!
echo "========================================"
echo "✅ ALL TESTS PASSED!"
echo "========================================"
echo ""
echo "Container is running successfully!"
echo ""
echo "Next steps:"
echo "  1. Push to Docker Hub:"
echo "     docker push $IMAGE_NAME"
echo ""
echo "  2. Update RunPod pod with new image"
echo ""
echo "To interact with container:"
echo "  docker exec -it $CONTAINER_NAME bash"
echo ""
echo "To stop container:"
echo "  docker rm -f $CONTAINER_NAME"
echo ""

