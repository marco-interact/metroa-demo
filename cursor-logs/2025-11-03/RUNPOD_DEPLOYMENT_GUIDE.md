# RunPod Deployment Guide - 2025-11-03

## Pod Configuration

- **Pod ID**: `xhqt6a1roo8mrc` (colmap_worker_gpu)
- **Storage Volume ID**: `rrtms4xkiz` (colmap-gpu-volume)
- **GitHub Repo**: https://github.com/marco-interact/colmap-demo.git
- **Vercel Team ID**: `team_PWckdPO4Vl3C1PWOA9qs9DrI` (interact-hq)

---

## Step 1: Initial Pod Setup

### Connect to RunPod Terminal

```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Install essential dependencies
apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    ninja-build \
    libboost-all-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    python3-pip \
    sqlite3
```

---

## Step 2: Install COLMAP

### Option A: From Source (Recommended for GPU optimization)

```bash
# Navigate to workspace
cd /workspace

# Clone COLMAP repository
git clone https://github.com/colmap/colmap.git
cd colmap

# Create build directory
mkdir build && cd build

# Configure with CMake (GPU enabled)
cmake .. -GNinja \
    -DCMAKE_CUDA_ARCHITECTURES=native \
    -DCMAKE_BUILD_TYPE=Release

# Build COLMAP
ninja && ninja install

# Verify installation
colmap -h
```

### Option B: Pre-built Binary (Faster setup)

```bash
# Download pre-built COLMAP
cd /workspace
wget https://github.com/colmap/colmap/releases/download/3.9.1/COLMAP-3.9.1-linux.tar.gz
tar -xzf COLMAP-3.9.1-linux.tar.gz
export PATH="/workspace/colmap/bin:$PATH"

# Add to .bashrc for persistence
echo 'export PATH="/workspace/colmap/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
colmap -h
```

---

## Step 3: Clone and Setup Application

```bash
# Navigate to persistent storage
cd /workspace

# Clone the repository
git clone https://github.com/marco-interact/colmap-demo.git
cd colmap-demo

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/results data/cache data/uploads

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)

# Add environment variables to .bashrc
cat >> ~/.bashrc << 'EOF'

# COLMAP Application Environment
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1
EOF

source ~/.bashrc
```

---

## Step 4: Initialize Database

```bash
cd /workspace/colmap-demo

# Activate virtual environment
source venv/bin/activate

# Initialize the database with demo data
python3 -c "
import asyncio
from database import Database

async def init_db():
    db = Database()
    await db.initialize()
    print('Database initialized successfully!')

asyncio.run(init_db())
"
```

---

## Step 5: Start Backend Server

```bash
cd /workspace/colmap-demo
source venv/bin/activate

# Start the FastAPI backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: `http://xhqt6a1roo8mrc-8000.proxy.runpod.net`

---

## Step 6: Deploy Frontend to Vercel

### Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### Deploy Frontend

```bash
cd /workspace/colmap-demo

# Install Node dependencies
npm install

# Build the application
npm run build

# Deploy to Vercel (with team)
vercel --prod --yes \
    --token YOUR_VERCEL_TOKEN \
    --scope interact-hq

# Or link to existing project
vercel link --scope interact-hq --yes
vercel --prod --yes
```

### Set Environment Variables in Vercel

Go to your Vercel project settings and add:

```
NEXT_PUBLIC_API_URL=http://xhqt6a1roo8mrc-8000.proxy.runpod.net
```

---

## Step 7: Auto-start Setup (Optional)

Create a startup script that runs on pod initialization:

```bash
cat > /workspace/start-colmap.sh << 'EOF'
#!/bin/bash

# Navigate to project
cd /workspace/colmap-demo

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Start the backend server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x /workspace/start-colmap.sh

# Run the script
/workspace/start-colmap.sh
```

---

## Testing the Deployment

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# List projects (demo scans should appear)
curl http://localhost:8000/api/projects

# Test specific demo scan
curl http://localhost:8000/api/projects/demoscan-dollhouse
```

### Test COLMAP Processing

```bash
# Test COLMAP installation
colmap -h

# Test GPU availability
nvidia-smi

# Run COLMAP test
cd /workspace/colmap-demo/scripts/test
./test-colmap-simple.sh
```

---

## Troubleshooting

### COLMAP Not Found

```bash
# Find COLMAP binary
find /workspace -name colmap -type f

# Add to PATH
export PATH="/path/to/colmap/bin:$PATH"
```

### Database Issues

```bash
# Reset database
rm -f /workspace/colmap-demo/data/database.db
python3 -c "import asyncio; from database import Database; asyncio.run(Database().initialize())"
```

### Port Already in Use

```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Storage Volume Not Mounted

```bash
# Check volume status
df -h | grep workspace

# Ensure volume ID matches: rrtms4xkiz
```

---

## Monitoring

### Check Backend Logs

```bash
cd /workspace/colmap-demo
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
```

### Monitor GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi
```

### Check Storage Usage

```bash
# Check disk space
df -h /workspace

# Check data directory size
du -sh /workspace/colmap-demo/data/*
```

---

## Quick Commands Reference

```bash
# Start backend server
cd /workspace/colmap-demo && source venv/bin/activate && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Restart backend
lsof -ti:8000 | xargs kill -9 && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Update code from GitHub
cd /workspace/colmap-demo && git pull origin main

# Rebuild dependencies
cd /workspace/colmap-demo && source venv/bin/activate && pip install -r requirements.txt

# View logs
tail -f /workspace/colmap-demo/logs/app.log

# Check COLMAP version
colmap -h | head -n 1
```

---

## Pod Endpoints

- **Backend API**: http://xhqt6a1roo8mrc-8000.proxy.runpod.net
- **Frontend (Vercel)**: Will be provided after deployment
- **Pod SSH**: Available through RunPod dashboard

---

*Deployment Guide Generated: 2025-11-03*

