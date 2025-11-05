#!/bin/bash
################################################################################
# Install Supervisor to Keep Backend Running Permanently
# Works in Docker containers without systemd
################################################################################

set -e

echo "=========================================="
echo "🔧 Installing Supervisor Process Manager"
echo "=========================================="
echo ""

# Install supervisor
echo "📦 Installing supervisor..."
apt-get update
apt-get install -y supervisor

echo "✅ Supervisor installed"
echo ""

# Create supervisor config for Xvfb
echo "📝 Creating Xvfb supervisor config..."
cat > /etc/supervisor/conf.d/xvfb.conf << 'EOF'
[program:xvfb]
command=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset
autostart=true
autorestart=true
startsecs=5
stdout_logfile=/workspace/xvfb.log
stderr_logfile=/workspace/xvfb.log
EOF

# Create supervisor config for COLMAP backend
echo "📝 Creating COLMAP backend supervisor config..."
cat > /etc/supervisor/conf.d/colmap-backend.conf << 'EOF'
[program:colmap-backend]
command=/workspace/colmap-demo/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
directory=/workspace/colmap-demo
autostart=true
autorestart=true
startsecs=10
stdout_logfile=/workspace/server.log
stderr_logfile=/workspace/server.log
environment=
    DISPLAY=":99",
    QT_QPA_PLATFORM="offscreen",
    MESA_GL_VERSION_OVERRIDE="3.3",
    CUDA_VISIBLE_DEVICES="0",
    STORAGE_DIR="/workspace/data/results",
    DATABASE_PATH="/workspace/colmap-demo/data/database.db",
    CACHE_DIR="/workspace/data/cache",
    UPLOADS_DIR="/workspace/data/uploads",
    COLMAP_PATH="/usr/bin/colmap",
    PYTHONUNBUFFERED="1"
EOF

echo "✅ Supervisor configs created"
echo ""

# Stop existing processes
echo "🛑 Stopping existing processes..."
killall -9 python3 uvicorn Xvfb 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 3

# Start supervisor
echo "🚀 Starting supervisor..."
service supervisor start || supervisord -c /etc/supervisor/supervisord.conf

sleep 3

# Reload supervisor configs
supervisorctl reread
supervisorctl update

sleep 3

# Check status
echo ""
echo "📊 Service Status:"
supervisorctl status

echo ""
echo "🧪 Testing backend..."
sleep 5

HEALTH=$(curl -s http://localhost:8000/health)
if [ ! -z "$HEALTH" ]; then
    echo "✅ Backend is healthy!"
    echo "$HEALTH"
else
    echo "⚠️  Backend starting... check logs:"
    echo "tail -f /workspace/server.log"
fi

echo ""
echo "=========================================="
echo "✨ Installation Complete!"
echo "=========================================="
echo ""
echo "📋 Supervisor Management:"
echo "  • Status:  supervisorctl status"
echo "  • Start:   supervisorctl start colmap-backend"
echo "  • Stop:    supervisorctl stop colmap-backend"
echo "  • Restart: supervisorctl restart colmap-backend"
echo "  • Logs:    tail -f /workspace/server.log"
echo ""
echo "🔄 Auto-start: ✅ Enabled"
echo "🔄 Auto-restart: ✅ Enabled"
echo ""
echo "🌐 Endpoints:"
echo "  • Local:  http://localhost:8000/health"
echo "  • Public: https://xhqt6a1roo8mrc-8000.proxy.runpod.net/health"
echo ""

