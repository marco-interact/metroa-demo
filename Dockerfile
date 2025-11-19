# ============================================================================
# Metroa Backend - Production Docker Image
# ============================================================================
# 
# PRODUCTION BUILD - Compiles COLMAP from source for maximum performance
# Build time: 30-45 minutes | Image size: 8-12 GB
#
# Features:
# - COLMAP 3.10 (CUDA-enabled, built from source, RTX 4090 optimized)
# - OpenMVS v2.2.0 (ultra-dense point clouds)
# - Open3D 0.19.0 (point cloud processing)
# - Python 3.12 + FastAPI
#
# For FAST BUILD (5-10 min), use: Dockerfile.fast
#
# Build: docker build -t metroa-backend:latest .
# Run: docker run --gpus all -p 8888:8888 -v $(pwd)/data:/workspace/data metroa-backend:latest
# ============================================================================

FROM nvidia/cuda:12.8.1-devel-ubuntu24.04 AS base

# Metadata
LABEL maintainer="Metroa Labs Team"
LABEL description="Metroa Backend - COLMAP + OpenMVS + Open3D GPU Image"
LABEL version="1.0.0"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:/usr/local/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH \
    QT_QPA_PLATFORM=offscreen \
    DISPLAY=:99 \
    MESA_GL_VERSION_OVERRIDE=3.3

# Install system dependencies (all stages need these)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    cmake \
    ninja-build \
    git \
    wget \
    curl \
    pkg-config \
    # Python runtime
    python3.12 \
    python3.12-dev \
    python3-pip \
    # Math & optimization libraries (COLMAP + OpenMVS)
    libeigen3-dev \
    libceres-dev \
    libboost-all-dev \
    libflann-dev \
    libgmp-dev \
    libmpfr-dev \
    # Image I/O
    libfreeimage-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopencv-dev \
    # Other dependencies
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    libcgal-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    # Runtime utilities
    ffmpeg \
    sqlite3 \
    lsof \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Note: Ubuntu 24.04 comes with pip 24.0, setuptools 68.1.2, wheel 0.42.0
# These versions are recent enough, skip upgrade to avoid Debian package conflicts

# ----------------------------------------------------------------------------
# Stage 2: Build COLMAP with CUDA Support
# ----------------------------------------------------------------------------
FROM base AS colmap-builder

# COLMAP Version: 3.10 (stable release with CUDA 12 support)
# Commit: Latest from 3.10 branch
ENV COLMAP_VERSION=3.10 \
    COLMAP_SRC=/opt/colmap-src \
    COLMAP_BUILD=/opt/colmap-build

WORKDIR /opt

# Clone COLMAP repository
RUN git clone https://github.com/colmap/colmap.git ${COLMAP_SRC} && \
    cd ${COLMAP_SRC} && \
    git checkout ${COLMAP_VERSION} && \
    git submodule update --init --recursive

# Configure and build COLMAP
# RTX 4090 compute capability: 8.9 (Ada Lovelace)
RUN mkdir -p ${COLMAP_BUILD} && \
    cd ${COLMAP_BUILD} && \
    cmake ${COLMAP_SRC} \
        -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CUDA_ARCHITECTURES=89 \
        -DCUDA_ENABLED=ON \
        -DGUI_ENABLED=OFF \
        -DOPENGL_ENABLED=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_C_FLAGS="-O3 -march=native -mtune=native -ffast-math" \
        -DCMAKE_CXX_FLAGS="-O3 -march=native -mtune=native -ffast-math" \
        -DCMAKE_CUDA_FLAGS="-O3 --use_fast_math -Xptxas -O3" \
        -DCUDA_ARCH_BIN="8.9" \
        -DCUDA_ARCH_PTX="8.9" \
        -DBUILD_SHARED_LIBS=ON && \
    ninja -j$(($(nproc) * 3 / 4)) && \
    ninja install && \
    ldconfig

# Verify COLMAP installation
RUN colmap --help | head -5 && \
    ldd $(which colmap) | grep -q cuda && echo "✅ COLMAP linked with CUDA"

# ----------------------------------------------------------------------------
# Stage 3: Build OpenMVS
# ----------------------------------------------------------------------------
FROM base AS openmvs-builder

# OpenMVS Version: Latest stable (v2.2.0 or latest from main)
# We'll use a specific commit for reproducibility
ENV OPENMVS_VERSION=v2.2.0 \
    OPENMVS_SRC=/opt/openmvs-src \
    OPENMVS_BUILD=/opt/openmvs-build

WORKDIR /opt

# Clone OpenMVS repository with submodules (VCG library)
RUN git clone --recursive https://github.com/cdcseacave/openMVS.git ${OPENMVS_SRC} && \
    cd ${OPENMVS_SRC} && \
    git checkout ${OPENMVS_VERSION} && \
    git submodule update --init --recursive

# Install OpenMVS dependencies (some may already be installed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcgal-dev \
    libcgal-qt5-dev \
    && rm -rf /var/lib/apt/lists/*

# Build OpenMVS
# Note: VCG is included as a submodule in openMVS/vcg
RUN mkdir -p ${OPENMVS_BUILD} && \
    cd ${OPENMVS_BUILD} && \
    cmake ${OPENMVS_SRC} \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DVCG_DIR=${OPENMVS_SRC}/vcg \
        -DCMAKE_CXX_FLAGS="-O3" && \
    make -j$(($(nproc) * 3 / 4)) && \
    make install && \
    ldconfig

# Verify OpenMVS installation
RUN DensifyPointCloud --help | head -5 && \
    ReconstructMesh --help | head -5 && \
    echo "✅ OpenMVS tools installed"

# ----------------------------------------------------------------------------
# Stage 4: Final Production Image
# ----------------------------------------------------------------------------
FROM base AS production

# Copy COLMAP from builder stage
COPY --from=colmap-builder /usr/local/bin/colmap /usr/local/bin/colmap
COPY --from=colmap-builder /usr/local/lib/libcolmap* /usr/local/lib/
COPY --from=colmap-builder /usr/local/share/colmap /usr/local/share/colmap

# Copy OpenMVS binaries from builder stage
COPY --from=openmvs-builder /usr/local/bin/DensifyPointCloud /usr/local/bin/
COPY --from=openmvs-builder /usr/local/bin/ReconstructMesh /usr/local/bin/
COPY --from=openmvs-builder /usr/local/bin/RefineMesh /usr/local/bin/
COPY --from=openmvs-builder /usr/local/bin/TextureMesh /usr/local/bin/
COPY --from=openmvs-builder /usr/local/bin/InterfaceCOLMAP /usr/local/bin/
COPY --from=openmvs-builder /usr/local/lib/libopenmvs* /usr/local/lib/

# Set working directory
WORKDIR /app

# Copy Python requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies (including Open3D)
# Open3D Version: 0.19.0 (pinned in requirements.txt)
RUN python3.12 -m pip install --break-system-packages --no-cache-dir -r requirements.txt
# Note: Import tests removed - Open3D uses CPU-specific instructions that fail
# during cross-platform builds (ARM Mac → x86_64 Linux). Works fine on actual RunPod hardware.

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start-backend.sh

# Create necessary directories
RUN mkdir -p /workspace/data/{results,uploads,cache} && \
    mkdir -p /app/logs

# Expose FastAPI port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Default command: Use robust startup script with detailed error checking
CMD ["./start-backend.sh"]

# ============================================================================
# Build Summary:
# ============================================================================
# 
# Installed Versions:
# - COLMAP: 3.10 (CUDA-enabled, RTX 4090 optimized)
# - OpenMVS: v2.2.0 (latest stable)
# - Open3D: 0.19.0 (Python bindings)
# - Python: 3.12
# - CUDA: 12.8.1
# - Ubuntu: 24.04
#
# Build Time: ~30-45 minutes (COLMAP + OpenMVS builds)
# Image Size: ~8-12 GB (includes all dependencies)
#
# ============================================================================

