# Metroa Backend - Makefile
# Convenient commands for building and managing the Docker image

.PHONY: help build build-push test run clean verify

# Image configuration
IMAGE_NAME = metroa-backend
TAG = latest
DOCKERFILE = Dockerfile

# Default target
help:
	@echo "Metroa Backend - Docker Build Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make build          - Build Docker image (tag: latest)"
	@echo "  make build TAG=v1.0 - Build with specific tag"
	@echo "  make build-push     - Build and push to registry"
	@echo "  make test           - Test image locally (requires GPU)"
	@echo "  make run            - Run container locally"
	@echo "  make verify         - Verify installed tools"
	@echo "  make clean          - Remove local image"
	@echo "  make help           - Show this help message"
	@echo ""

# Build Docker image
build:
	@echo "🔨 Building $(IMAGE_NAME):$(TAG)..."
	@./docker-build.sh $(TAG)

# Build and push to registry
build-push:
	@echo "🔨 Building and pushing $(IMAGE_NAME):$(TAG)..."
	@./docker-build.sh $(TAG) --push

# Test image locally (requires GPU)
test:
	@echo "🧪 Testing image..."
	@docker run --rm --gpus all $(IMAGE_NAME):$(TAG) \
		sh -c "colmap --help | head -3 && \
		       DensifyPointCloud --help | head -3 && \
		       python3.12 -c 'import open3d; print(\"Open3D:\", open3d.__version__)'"

# Run container locally
run:
	@echo "🚀 Running container..."
	@docker run --rm -it --gpus all \
		-p 8888:8888 \
		-v $$(pwd)/data:/workspace/data \
		$(IMAGE_NAME):$(TAG)

# Verify installed tools in image
verify:
	@echo "✅ Verifying installed tools..."
	@docker run --rm --gpus all $(IMAGE_NAME):$(TAG) \
		sh -c "echo '=== COLMAP ===' && \
		       colmap --help | head -3 && \
		       echo '' && \
		       echo '=== OpenMVS ===' && \
		       DensifyPointCloud --help | head -3 && \
		       echo '' && \
		       echo '=== Open3D ===' && \
		       python3.12 -c 'import open3d; print(\"Version:\", open3d.__version__)' && \
		       echo '' && \
		       echo '=== FastAPI ===' && \
		       python3.12 -c 'import fastapi; print(\"Version:\", fastapi.__version__)'"

# Clean local image
clean:
	@echo "🧹 Removing local image..."
	@docker rmi $(IMAGE_NAME):$(TAG) || echo "Image not found"

# Show image info
info:
	@docker images $(IMAGE_NAME):$(TAG) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

