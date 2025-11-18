#!/bin/bash
# Start backend in screen session

cd /workspace/metroa-demo

# Kill any existing backend
pkill -f "python.*main.py"

# Start in screen session
screen -S metroa-backend -d -m python main.py

# Wait a moment
sleep 2

# Check if backend is running
if curl -s http://localhost:8888/health > /dev/null; then
    echo "✅ Backend started successfully!"
    echo "   Attach to screen: screen -r metroa-backend"
    echo "   Detach: Ctrl+A then D"
else
    echo "⚠️  Backend may still be starting..."
    echo "   Attach to screen to check: screen -r metroa-backend"
fi
