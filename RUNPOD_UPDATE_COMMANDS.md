# RunPod Update Commands

## Current Status
- ✅ Backend running on pod `0pgs4gpmkmkn5y`
- ✅ Persistent storage verified (503TB available)
- ✅ Demo data confirmed (1 project, 2 scans)
- ✅ Cloudflare tunnel: `https://eligibility-hart-baking-conservation.trycloudflare.com`
- ✅ Vercel updated with tunnel URL

---

## Pull Latest Code from GitHub

Run in RunPod web terminal:

```bash
cd /workspace/colmap-mvp
source venv/bin/activate
git fetch origin
git reset --hard origin/main
```

---

## Restart Backend (if needed)

```bash
cd /workspace/colmap-mvp
source venv/bin/activate
pkill -f "python.*main.py"
export PORT=8000
nohup python main.py > backend.log 2>&1 &
sleep 8
curl http://localhost:8000/health
```

---

## Restart Cloudflare Tunnel (if URL changes)

```bash
pkill -f cloudflared
nohup cloudflared tunnel --url http://localhost:8000 --protocol quic > /tmp/cloudflared.log 2>&1 &
sleep 10
grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -1
```

**If tunnel URL changes, update Vercel:**

1. Copy new tunnel URL
2. Vercel Dashboard → Project Settings → Environment Variables
3. Update `NEXT_PUBLIC_API_URL` = new tunnel URL
4. Redeploy

---

## Verify Everything

```bash
# Backend health
curl http://localhost:8000/health

# Demo data
curl http://localhost:8000/api/projects | jq

# Tunnel (external)
curl https://eligibility-hart-baking-conservation.trycloudflare.com/health
```

---

## Quick Troubleshooting

### Backend not responding
```bash
cd /workspace/colmap-mvp
source venv/bin/activate
tail -n 100 backend.log
```

### Database issues
```bash
ls -la /workspace/database.db
sqlite3 /workspace/database.db "SELECT COUNT(*) FROM projects;"
```

### Tunnel not working
```bash
tail -n 50 /tmp/cloudflared.log
ps aux | grep cloudflared
```

---

**Current Tunnel**: https://eligibility-hart-baking-conservation.trycloudflare.com  
**Pod ID**: 0pgs4gpmkmkn5y  
**Backend Port**: 8000

