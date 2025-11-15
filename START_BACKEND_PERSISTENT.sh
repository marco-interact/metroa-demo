#!/bin/bash
# Start Metroa Backend in a persistent way that survives terminal disconnection

set -e

cd /workspace/metroa-demo

# Kill any existing backend on port 8888
echo "🔍 Checking for existing backend..."
lsof -ti :8888 | xargs kill -9 2>/dev/null || true
fuser -k 8888/tcp 2>/dev/null || true
pkill -9 -f "python.*main.py" 2>/dev/null || true
sleep 2

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main || true

# Method 1: Using screen (recommended - allows reconnection)
if command -v screen > /dev/null 2>&1; then
    echo "🖥️  Starting backend in screen session 'metroa-backend'..."
    screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py"
    echo "✅ Backend started in screen session"
    echo ""
    echo "To reconnect to the session:"
    echo "  screen -r metroa-backend"
    echo ""
    echo "To detach from session (keep running):"
    echo "  Press Ctrl+A then D"
    echo ""
    echo "To view all sessions:"
    echo "  screen -ls"
    
# Method 2: Using nohup (fallback)
elif command -v nohup > /dev/null 2>&1; then
    echo "🚀 Starting backend with nohup..."
    nohup python main.py > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    echo "Logs are in: backend.log"
    echo ""
    echo "To view logs:"
    echo "  tail -f backend.log"
    echo ""
    echo "To stop backend:"
    echo "  kill $BACKEND_PID"
    
# Method 3: Using systemd (if available)
elif systemctl --version > /dev/null 2>&1; then
    echo "⚙️  Starting backend with systemd..."
    # Create a simple systemd service (if not exists)
    cat > /tmp/metroa-backend.service << EOF
[Unit]
Description=Metroa Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/metroa-demo
ExecStart=/usr/bin/python3 /workspace/metroa-demo/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    sudo cp /tmp/metroa-backend.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable metroa-backend
    sudo systemctl start metroa-backend
    echo "✅ Backend started as systemd service"
    echo ""
    echo "To check status:"
    echo "  sudo systemctl status metroa-backend"
    echo ""
    echo "To view logs:"
    echo "  sudo journalctl -u metroa-backend -f"
    
# Fallback: Just start in background
else
    echo "⚠️  No screen/nohup/systemd available, starting in background..."
    python main.py &
    BACKEND_PID=$!
    echo "✅ Backend started with PID: $BACKEND_PID"
    echo "⚠️  WARNING: This may not persist after terminal closes"
    echo "Install screen for better persistence: apt-get install -y screen"
fi

# Wait a moment and test
sleep 3
echo ""
echo "🧪 Testing backend..."
if curl -s http://localhost:8888/health > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
    curl http://localhost:8888/health
else
    echo "⚠️  Backend may still be starting, check logs"
fi

echo ""
echo "📊 Backend status:"
ps aux | grep "python.*main.py" | grep -v grep || echo "No backend process found"

