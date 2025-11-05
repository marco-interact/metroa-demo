#!/bin/bash
################################################################################
# Resume RunPod CI/CD - Complete Backend Startup
# Fixes: Frontend failing to connect to backend (502 Bad Gateway)
# Date: 2025-11-05
################################################################################

set -e  # Exit on error

echo "=================================================="
echo "🔄 Resuming RunPod CI/CD Deployment"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC}  $1"
}

print_error() {
    echo -e "${RED}❌${NC}  $1"
}

################################################################################
# Step 1: Check if we're on RunPod
################################################################################

print_step "Step 1/6: Verifying RunPod environment..."

if [ ! -d "/workspace" ]; then
    print_error "Not running on RunPod (no /workspace directory)"
    echo "This script should be run on your RunPod instance."
    echo ""
    echo "To deploy:"
    echo "1. SSH into your RunPod pod"
    echo "2. Run this script"
    exit 1
fi

print_info "✅ RunPod environment confirmed"

################################################################################
# Step 2: Pull Latest Code
################################################################################

print_step "Step 2/6: Pulling latest code from GitHub..."

cd /workspace/colmap-demo

# Stash any local changes
git stash save "Auto-stash before pull $(date +%Y%m%d_%H%M%S)"

# Pull latest changes
git pull origin main

print_info "✅ Code updated"

################################################################################
# Step 3: Update Python Dependencies
################################################################################

print_step "Step 3/6: Updating Python dependencies..."

# Activate virtual environment
source /workspace/colmap-demo/venv/bin/activate

# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt

print_info "✅ Python dependencies updated"

################################################################################
# Step 4: Verify COLMAP Installation
################################################################################

print_step "Step 4/6: Verifying COLMAP installation..."

if command -v colmap &> /dev/null; then
    COLMAP_VERSION=$(colmap -h 2>&1 | head -n 1)
    print_info "✅ COLMAP installed: $COLMAP_VERSION"
else
    print_error "COLMAP not found!"
    echo "Please install COLMAP first by running:"
    echo "  bash /workspace/colmap-demo/runpod-install-colmap.sh"
    exit 1
fi

################################################################################
# Step 5: Initialize Database
################################################################################

print_step "Step 5/6: Initializing database..."

cd /workspace/colmap-demo
source venv/bin/activate

# Set environment variables
export STORAGE_DIR=/workspace/colmap-demo/data/results
export DATABASE_PATH=/workspace/colmap-demo/data/database.db
export CACHE_DIR=/workspace/colmap-demo/data/cache
export UPLOADS_DIR=/workspace/colmap-demo/data/uploads
export COLMAP_PATH=$(which colmap)
export PYTHONUNBUFFERED=1

# Create directories
mkdir -p data/results data/cache data/uploads

# Initialize database and setup demo data
python3 << 'PYEOF'
from database import Database

# Create database instance (auto-initializes tables)
db = Database()
print('✅ Database tables initialized!')

# Setup demo data
result = db.setup_demo_data()
if result['status'] == 'success':
    print(f"✅ Demo data setup: {result['message']}")
    print(f"   Project ID: {result['project_id']}")
    print(f"   Scan IDs: {', '.join(result['scan_ids'])}")
else:
    print(f"⚠️  Demo data setup: {result.get('message', 'Unknown error')}")
PYEOF

print_info "✅ Database initialized"

################################################################################
# Step 6: Start Backend Server
################################################################################

print_step "Step 6/6: Starting backend server..."

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Get Pod ID for public URL
POD_ID=$(hostname)
PUBLIC_URL="https://${POD_ID}-8000.proxy.runpod.net"

print_info "📡 Starting backend server..."
print_info "   Local: http://0.0.0.0:8000"
print_info "   Public: $PUBLIC_URL"

# Start server in background with nohup
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /workspace/colmap-demo/backend.log 2>&1 &

# Save PID
echo $! > /workspace/colmap-demo/backend.pid

# Wait a moment for server to start
sleep 5

# Test if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    print_info "✅ Backend server started successfully!"
else
    print_error "Backend server failed to start. Check logs:"
    echo "   tail -f /workspace/colmap-demo/backend.log"
    exit 1
fi

################################################################################
# Deployment Complete
################################################################################

echo ""
echo "=================================================="
echo "✨ RunPod Backend Deployment Complete!"
echo "=================================================="
echo ""
echo "📋 Backend Status:"
echo "   • Server PID: $(cat /workspace/colmap-demo/backend.pid)"
echo "   • Local URL: http://localhost:8000"
echo "   • Public URL: $PUBLIC_URL"
echo ""
echo "📋 Test the Backend:"
echo "   curl $PUBLIC_URL/health"
echo ""
echo "📋 View Logs:"
echo "   tail -f /workspace/colmap-demo/backend.log"
echo ""
echo "📋 Stop Backend:"
echo "   kill \$(cat /workspace/colmap-demo/backend.pid)"
echo ""
echo "=================================================="
echo ""
echo "🌐 Next Step: Update Frontend Environment"
echo ""
echo "Run on your LOCAL machine:"
echo "   cd /Users/marco.aurelio/Desktop/colmap-demo"
echo "   echo 'NEXT_PUBLIC_API_URL=\"$PUBLIC_URL\"' > .env.production"
echo "   vercel --prod"
echo ""
echo "=================================================="

