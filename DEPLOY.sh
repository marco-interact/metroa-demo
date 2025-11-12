#!/bin/bash
################################################################################
# Quick Deployment Script for Metroa Demo
# Frontend: Vercel | Backend: RunPod RTX 4090
################################################################################

echo "=============================================="
echo "🚀 Metroa Demo - Deployment Script"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

################################################################################
# FRONTEND DEPLOYMENT (Run this locally)
################################################################################

if [ "$1" == "frontend" ]; then
    echo -e "${BLUE}📦 Deploying Frontend to Vercel...${NC}"
    echo ""
    
    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Installing Vercel CLI...${NC}"
        npm install -g vercel
    fi
    
    # Deploy
    echo -e "${BLUE}Deploying to production...${NC}"
    vercel --prod
    
    echo ""
    echo -e "${GREEN}✅ Frontend deployment initiated!${NC}"
    echo "Check status at: https://vercel.com/marco-interact/metroa-demo"
    exit 0
fi

################################################################################
# BACKEND DEPLOYMENT (Run this on RunPod)
################################################################################

if [ "$1" == "backend" ]; then
    echo -e "${BLUE}🖥️  Deploying Backend on RunPod...${NC}"
    echo ""
    
    # Step 1: Pull latest code
    echo -e "${BLUE}Step 1: Pulling latest code...${NC}"
    git pull origin main
    echo ""
    
    # Step 2: Rebuild COLMAP with optimizations
    echo -e "${BLUE}Step 2: Rebuilding COLMAP with RTX 4090 optimizations...${NC}"
    echo -e "${YELLOW}This will take 10-15 minutes...${NC}"
    bash build-colmap-gpu-fixed.sh
    echo ""
    
    # Step 3: Install Python dependencies
    echo -e "${BLUE}Step 3: Installing Python dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo ""
    
    # Step 4: Create directories
    echo -e "${BLUE}Step 4: Creating data directories...${NC}"
    mkdir -p data/{uploads,cache,results}
    mkdir -p data/cache/{jobs,thumbnails}
    mkdir -p logs
    chmod -R 755 data/
    echo ""
    
    # Step 5: Verify COLMAP
    echo -e "${BLUE}Step 5: Verifying COLMAP installation...${NC}"
    if command -v colmap &> /dev/null; then
        echo -e "${GREEN}✅ COLMAP found at: $(which colmap)${NC}"
        colmap -h | head -5
    else
        echo -e "${RED}❌ COLMAP not found!${NC}"
        exit 1
    fi
    echo ""
    
    # Step 6: Check GPU
    echo -e "${BLUE}Step 6: Checking GPU...${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
    
    # Step 7: Test backend
    echo -e "${BLUE}Step 7: Testing backend startup...${NC}"
    echo "Starting server (Ctrl+C to stop)..."
    python main.py
    
    exit 0
fi

################################################################################
# FULL DEPLOYMENT (Backend then Frontend)
################################################################################

if [ "$1" == "all" ]; then
    echo -e "${YELLOW}This must be run in two stages:${NC}"
    echo ""
    echo "1. On RunPod (backend):"
    echo "   bash DEPLOY.sh backend"
    echo ""
    echo "2. Locally (frontend):"
    echo "   bash DEPLOY.sh frontend"
    echo ""
    exit 0
fi

################################################################################
# USAGE
################################################################################

echo "Usage:"
echo "  bash DEPLOY.sh frontend   - Deploy frontend to Vercel (run locally)"
echo "  bash DEPLOY.sh backend    - Deploy backend on RunPod (run on pod)"
echo "  bash DEPLOY.sh all        - Show full deployment instructions"
echo ""
echo "Examples:"
echo "  # On your local machine:"
echo "  bash DEPLOY.sh frontend"
echo ""
echo "  # On your RunPod:"
echo "  bash DEPLOY.sh backend"
echo ""

