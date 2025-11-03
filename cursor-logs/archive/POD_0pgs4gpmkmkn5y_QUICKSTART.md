# Pod Setup: colmap_worker_gpu (0pgs4gpmkmkn5y)

## Pod Details
- **Name**: colmap_worker_gpu
- **ID**: 0pgs4gpmkmkn5y
- **SSH**: `ssh root@203.57.40.175 -p 10123`
- **Volume**: ✅ Attached (persistent storage)

---

## Quick Setup (All Commands)

### Step 1: SSH into Pod

From your Mac Terminal:
```bash
ssh root@203.57.40.175 -p 10123
```

If prompted about authenticity, type `yes`.

---

### Step 2: Run Complete Setup Script

Copy and paste this entire block:

```bash
cd /workspace && \
curl -s https://raw.githubusercontent.com/marco-interact/colmap-mvp/main/SETUP_POD_0pgs4gpmkmkn5y.sh | bash
```

Or run manually:

```bash
# Update system
apt-get update -qq

# Install COLMAP dependencies
apt-get install -y -qq \
    git cmake build-essential \
    libboost-program-options-dev libboost-filesystem-dev \
    libboost-graph-dev libboost-system-dev libboost-test-dev \
    libeigen3-dev libflann-dev libfreeimage-dev libmetis-dev \
    libgoogle-glog-dev libgflags-dev libsqlite3-dev libglew-dev \
    qtbase5-dev libqt5opengl5-dev libcgal-dev libceres-dev ffmpeg

# Install COLMAP
cd /tmp
git clone https://github.com/colmap/colmap.git
cd colmap && mkdir build && cd build
cmake .. -DCMAKE_CUDA_ARCHITECTURES=native
make -j$(nproc) && make install

# Clone repo
cd /workspace
git clone https://github.com/marco-interact/colmap-mvp.git
cd colmap-mvp

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start backend
nohup python main.py > backend.log 2>&1 &
sleep 8

# Verify
curl http://localhost:8000/health
curl http://localhost:8000/api/projects
```

---

### Step 3: Setup Cloudflare Tunnel

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -O /tmp/cloudflared.deb
apt-get install -y /tmp/cloudflared.deb

# Start tunnel
pkill -f cloudflared || true
nohup cloudflared tunnel --url http://localhost:8000 --protocol quic > /tmp/cloudflared.log 2>&1 &
sleep 10

# Get URL
grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -1
```

**Copy the tunnel URL!**

---

### Step 4: Update Vercel

1. Go to Vercel Dashboard
2. Project Settings → Environment Variables
3. Update `NEXT_PUBLIC_API_URL` = [tunnel URL from Step 3]
4. Redeploy

---

## Verify Everything

```bash
# Backend health
curl http://localhost:8000/health

# Demo data
curl http://localhost:8000/api/projects

# Should return 1 project with 2 scans
```

---

## Quick Restart (Future Use)

```bash
cd /workspace/colmap-mvp
source venv/bin/activate
pkill -f "python.*main.py" || true
git pull origin main
nohup python main.py > backend.log 2>&1 &
curl http://localhost:8000/health
```

---

## Troubleshooting

### Can't SSH
- Check SSH key is added in RunPod Settings
- Try: `ssh -v root@203.57.40.175 -p 10123`

### Backend won't start
- Check logs: `tail -f /workspace/colmap-mvp/backend.log`
- Check port: `ss -lntp | grep 8000`

### Tunnel won't start
- Check cloudflared: `ps aux | grep cloudflared`
- View logs: `tail -f /tmp/cloudflared.log`

---

**Status**: Ready for setup ✅

