#!/bin/bash
################################################################################
# RunPod Diagnostic and Auto-Fix Script
# Run this in your RunPod terminal to diagnose and fix all issues
################################################################################

echo "=================================="
echo "🔍 COLMAP Backend Diagnostic Tool"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Storage Volume
echo -e "${YELLOW}📁 Checking Storage Volume...${NC}"
if df -h | grep -q workspace; then
    echo -e "${GREEN}✅ Storage volume mounted${NC}"
    df -h | grep workspace
else
    echo -e "${RED}❌ Storage volume NOT mounted!${NC}"
    echo "Please attach volume rrtms4xkiz in RunPod settings"
    exit 1
fi
echo ""

# 2. Check Project Directory
echo -e "${YELLOW}📂 Checking Project Directory...${NC}"
if [ -d "/workspace/colmap-demo" ]; then
    echo -e "${GREEN}✅ Project directory exists${NC}"
    ls -la /workspace/colmap-demo/ | head -5
else
    echo -e "${RED}❌ Project directory missing! Cloning...${NC}"
    cd /workspace
    git clone https://github.com/marco-interact/colmap-demo.git
    cd colmap-demo
fi
echo ""

# 3. Check Virtual Environment
echo -e "${YELLOW}🐍 Checking Virtual Environment...${NC}"
if [ -d "/workspace/colmap-demo/venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    cd /workspace/colmap-demo
    python3 -m venv venv
fi
echo ""

# 4. Check if Server is Running
echo -e "${YELLOW}🖥️  Checking Server Status...${NC}"
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running on port 8000${NC}"
    ps aux | grep uvicorn | grep -v grep
    
    # Test health
    echo ""
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    HEALTH=$(curl -s http://localhost:8000/health)
    if [ ! -z "$HEALTH" ]; then
        echo -e "${GREEN}✅ Health check passed:${NC}"
        echo "$HEALTH"
    else
        echo -e "${RED}❌ Health check failed${NC}"
    fi
else
    echo -e "${RED}❌ Server NOT running${NC}"
    echo -e "${YELLOW}🔧 Starting server...${NC}"
    
    # Kill any zombie processes
    killall -9 python3 2>/dev/null || true
    sleep 2
    
    # Navigate to project
    cd /workspace/colmap-demo
    
    # Activate venv
    source venv/bin/activate
    
    # Create necessary directories
    mkdir -p /workspace/data/results /workspace/data/cache /workspace/data/uploads
    
    # Set environment variables
    export STORAGE_DIR=/workspace/data/results
    export DATABASE_PATH=/workspace/colmap-demo/data/database.db
    export CACHE_DIR=/workspace/data/cache
    export UPLOADS_DIR=/workspace/data/uploads
    export COLMAP_PATH=$(which colmap)
    export PYTHONUNBUFFERED=1
    
    # Start server in background
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/server.log 2>&1 &
    
    echo "Server starting with PID: $!"
    sleep 5
    
    # Test again
    echo ""
    echo -e "${YELLOW}Testing after startup...${NC}"
    HEALTH=$(curl -s http://localhost:8000/health)
    if [ ! -z "$HEALTH" ]; then
        echo -e "${GREEN}✅ Server started successfully!${NC}"
        echo "$HEALTH"
    else
        echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
        echo "tail /workspace/server.log"
        exit 1
    fi
fi
echo ""

# 5. Check Public Endpoint
echo -e "${YELLOW}🌐 Checking Public Endpoint...${NC}"
PUBLIC_HEALTH=$(curl -s https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health)
if [ ! -z "$PUBLIC_HEALTH" ]; then
    echo -e "${GREEN}✅ Public endpoint working!${NC}"
    echo "$PUBLIC_HEALTH"
else
    echo -e "${RED}❌ Public endpoint not responding${NC}"
    echo "This might take a minute to propagate. Try again in 30 seconds."
fi
echo ""

# 6. Summary
echo "=================================="
echo -e "${GREEN}✨ Diagnostic Complete!${NC}"
echo "=================================="
echo ""
echo "📋 Summary:"
echo "  • Storage: $(df -h | grep workspace | awk '{print $2}')"
echo "  • Project: /workspace/colmap-demo"
echo "  • Server: Running (PID: $(pgrep -f 'uvicorn main:app'))"
echo "  • Local: http://localhost:8000/health"
echo "  • Public: https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health"
echo ""
echo "📝 Logs: tail -f /workspace/server.log"
echo "🔄 Restart: killall python3 && cd /workspace/colmap-demo && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /workspace/server.log 2>&1 &"
echo ""

