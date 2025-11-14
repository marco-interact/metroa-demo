# 🚀 Setup Pod 8pexe48luksdw3 from RunPod Web Terminal

**If you're already inside a RunPod container, use this guide**

---

## ✅ Method 1: Use RunPod Web Terminal (Recommended)

1. **Go to RunPod Dashboard:**
   - Visit: https://www.runpod.io/console/pods
   - Find pod: `8pexe48luksdw3`
   - Click **"Connect"** → **"Web Terminal"**

2. **You're now in the pod terminal!** Run this command:

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git && cd metroa-demo && bash setup-pod-8pexe48luksdw3.sh
```

**That's it!** The script will handle everything automatically.

---

## ✅ Method 2: Direct Setup Commands

If you prefer to run commands manually, here's what the script does:

```bash
# 1. Install dependencies
apt-get update && apt-get install -y git python3-pip ffmpeg sqlite3 build-essential cmake ninja-build

# 2. Clone repo
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# 3. Setup Python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Build COLMAP (takes 10-15 min)
bash build-colmap-gpu-fixed.sh

# 5. Initialize database
python3 -c "from database import db; db.setup_demo_data()"

# 6. Start backend
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

---

## ✅ Method 3: Copy Setup Script to Pod

If you have access to the pod via web terminal:

```bash
# 1. Clone repo
cd /workspace
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo

# 2. Make script executable
chmod +x setup-pod-8pexe48luksdw3.sh

# 3. Run setup
bash setup-pod-8pexe48luksdw3.sh
```

---

## 🔍 Verify Setup

After setup completes, verify:

```bash
# Check backend is running
curl http://localhost:8888/health

# Check logs
tail -f /workspace/metroa-demo/backend.log

# Check GPU
nvidia-smi

# Check COLMAP
colmap -h
```

---

## 📋 Pod Details

- **Pod ID:** `8pexe48luksdw3`
- **Public URL:** `https://8pexe48luksdw3-8888.proxy.runpod.net`
- **Port:** 8888 (Backend API)
- **Port:** 8888 (Jupyter Lab)
- **Volume:** `metroa-volume` (mvmh2mg1pt)
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHNBJaFmISOLjiFilSH5ROHAzqyURW7j61vXnVhMebYn`
- **Jupyter Password:** `8mt1655csdm6mvvacmap`
- **SSH Gateway:** `ssh 8pexe48luksdw3-64411de4@ssh.runpod.io -i ~/.ssh/id_ed25519`
- **SSH Direct:** `ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519`

---

## 🌐 Update Frontend (From Your Mac)

After backend is running, update frontend from your Mac:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
bash update-frontend-pod-8pexe48luksdw3.sh
```

---

**Note:** The SSH key issue occurs when trying to SSH from within a RunPod container. Use the **Web Terminal** method instead - it's the easiest way!

