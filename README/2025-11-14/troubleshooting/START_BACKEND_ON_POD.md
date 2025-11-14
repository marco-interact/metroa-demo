# 🚀 Start Backend on RunPod Pod

**Pod is running - now start the backend**

---

## ⚡ Quick Start (Copy/Paste on RunPod Terminal)

**Run this entire command block:**

```bash
cd /workspace

# Check if repo exists
if [ -d "metroa-demo" ]; then
    echo "✅ Repository exists"
    cd metroa-demo
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/marco-interact/metroa-demo.git
    cd metroa-demo
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Kill any existing backend
echo "🛑 Stopping existing backend..."
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

# Create data directory if needed
mkdir -p /workspace/data

# Start backend
echo "🚀 Starting backend..."
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export MESA_GL_VERSION_OVERRIDE=3.3
export DATABASE_PATH=/workspace/data/database.db

nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid

# Wait for startup
sleep 5

# Test backend
echo ""
echo "🔍 Testing backend..."
if curl -s http://localhost:8888/health > /dev/null; then
    echo "✅ BACKEND IS RUNNING!"
    curl http://localhost:8888/health
else
    echo "❌ Backend failed to start. Check logs:"
    tail -30 backend.log
fi
```

---

## 🔍 If Backend Fails - Check Logs

```bash
cd /workspace/metroa-demo
tail -50 backend.log
```

---

## 🔧 Common Issues & Fixes

### Issue: ModuleNotFoundError
```bash
cd /workspace/metroa-demo
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Syntax Error
```bash
cd /workspace/metroa-demo
git pull origin main
```

### Issue: Port Already in Use
```bash
lsof -ti:8888 | xargs kill -9
sleep 2
```

### Issue: Database Path Error
```bash
mkdir -p /workspace/data
export DATABASE_PATH=/workspace/data/database.db
```

---

## ✅ Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8888/health

# Should return:
# {"status":"healthy","message":"Backend is running","database_path":"/workspace/data/database.db"}

# Check process
ps aux | grep uvicorn | grep -v grep

# Check logs
tail -f /workspace/metroa-demo/backend.log
```

---

## 🌐 Test Public URL

**From your Mac:**

```bash
curl https://8pexe48luksdw3-8888.proxy.runpod.net/health
```

---

## 📋 Full Setup (If Not Already Done)

If you need to run the complete setup script:

```bash
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo
chmod +x setup-pod-8pexe48luksdw3.sh
bash setup-pod-8pexe48luksdw3.sh
```

**Note:** This takes 15-20 minutes (COLMAP build)

