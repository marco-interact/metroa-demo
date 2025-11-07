#!/bin/bash
################################################################################
# Install COLMAP Backend as Permanent System Service
# Backend will auto-start on boot and auto-restart if it crashes
################################################################################

set -e

echo "=========================================="
echo "🔧 Installing COLMAP Backend Service"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Install Xvfb service
echo -e "${BLUE}📦 Creating Xvfb service...${NC}"
cat > /etc/systemd/system/xvfb.service << 'EOF'
[Unit]
Description=X Virtual Frame Buffer
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Xvfb service created${NC}"

# Step 2: Create COLMAP backend service
echo -e "${BLUE}🚀 Creating COLMAP Backend service...${NC}"
cat > /etc/systemd/system/colmap-backend.service << 'EOF'
[Unit]
Description=COLMAP 3D Reconstruction Backend
After=network.target xvfb.service
Requires=xvfb.service

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/colmap-demo
Environment="PATH=/workspace/colmap-demo/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:99"
Environment="QT_QPA_PLATFORM=offscreen"
Environment="MESA_GL_VERSION_OVERRIDE=3.3"
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="STORAGE_DIR=/workspace/data/results"
Environment="DATABASE_PATH=/workspace/colmap-demo/data/database.db"
Environment="CACHE_DIR=/workspace/data/cache"
Environment="UPLOADS_DIR=/workspace/data/uploads"
Environment="COLMAP_PATH=/usr/bin/colmap"
Environment="PYTHONUNBUFFERED=1"
ExecStartPre=/bin/sleep 3
ExecStart=/workspace/colmap-demo/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:/workspace/server.log
StandardError=append:/workspace/server.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ COLMAP Backend service created${NC}"
echo ""

# Step 3: Stop existing processes
echo -e "${BLUE}🛑 Stopping existing processes...${NC}"
killall -9 python3 uvicorn Xvfb 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 3

echo -e "${GREEN}✅ Old processes stopped${NC}"
echo ""

# Step 4: Reload systemd
echo -e "${BLUE}🔄 Reloading systemd...${NC}"
systemctl daemon-reload

# Step 5: Enable services
echo -e "${BLUE}⚙️  Enabling services...${NC}"
systemctl enable xvfb.service
systemctl enable colmap-backend.service

echo -e "${GREEN}✅ Services enabled (will auto-start on boot)${NC}"
echo ""

# Step 6: Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
systemctl start xvfb.service
sleep 2
systemctl start colmap-backend.service
sleep 5

echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 7: Check status
echo -e "${BLUE}📊 Service Status:${NC}"
echo ""
echo "Xvfb Service:"
systemctl status xvfb.service --no-pager | head -10
echo ""

echo "COLMAP Backend Service:"
systemctl status colmap-backend.service --no-pager | head -10
echo ""

# Step 8: Test
echo -e "${BLUE}🧪 Testing backend...${NC}"
sleep 3
HEALTH=$(curl -s http://localhost:8000/health)
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo "$HEALTH"
else
    echo -e "${YELLOW}⚠️  Backend not responding yet. Check logs:${NC}"
    echo "journalctl -u colmap-backend.service -n 50"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ Service Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Service Management Commands:"
echo ""
echo "  • Start:   systemctl start colmap-backend"
echo "  • Stop:    systemctl stop colmap-backend"
echo "  • Restart: systemctl restart colmap-backend"
echo "  • Status:  systemctl status colmap-backend"
echo "  • Logs:    journalctl -u colmap-backend -f"
echo ""
echo "🔄 Auto-start: ✅ Enabled (starts on pod boot)"
echo "🔄 Auto-restart: ✅ Enabled (restarts if crashes)"
echo ""
echo "🌐 Endpoints:"
echo "  • Local:  http://localhost:8000/health"
echo "  • Public: https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health"
echo ""





