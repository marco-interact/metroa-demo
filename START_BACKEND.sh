#!/bin/bash
# Quick backend start script for RunPod

# Option 1: Install screen and use it
if command -v screen &> /dev/null; then
    screen -S metroa-backend -d -m python main.py
    echo "✅ Backend started in screen session 'metroa-backend'"
    echo "   Attach with: screen -r metroa-backend"
    echo "   Detach with: Ctrl+A then D"
else
    # Option 2: Use nohup
    nohup python main.py > backend.log 2>&1 &
    echo "✅ Backend started with nohup (PID: $!)"
    echo "   Logs: tail -f backend.log"
    echo "   Stop: kill $!"
fi

# Wait a moment and check
sleep 2
if curl -s http://localhost:8888/health > /dev/null; then
    echo "✅ Backend is responding!"
else
    echo "⚠️  Backend may still be starting. Check logs."
fi
