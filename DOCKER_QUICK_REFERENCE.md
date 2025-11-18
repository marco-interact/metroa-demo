# 🐳 Docker Quick Reference - RunPod

## 🚀 ONE-TIME SETUP (30-45 minutes)

```bash
# SSH into RunPod, then run these 3 commands:
cd /workspace/metroa-demo
git pull origin main
bash README/scripts/build-docker-runpod.sh
```

**Wait for build to complete (30-45 min)**

---

## ▶️ START BACKEND (10 seconds)

```bash
cd /workspace/metroa-demo
bash README/scripts/run-docker-runpod.sh
```

**Backend will be running at:** `http://localhost:8888`

---

## ✅ VERIFY IT'S WORKING

```bash
curl http://localhost:8888/health
# Should return: {"status":"healthy","gpu_available":true}
```

---

## 📋 USEFUL COMMANDS

### View Logs
```bash
docker logs -f metroa-backend              # Live logs
docker logs metroa-backend --tail 50       # Last 50 lines
```

### Control Container
```bash
docker stop metroa-backend                 # Stop
docker start metroa-backend                # Start
docker restart metroa-backend              # Restart
docker rm -f metroa-backend                # Remove (keeps image)
```

### Check Status
```bash
docker ps --filter name=metroa-backend     # Running?
curl http://localhost:8888/health          # Healthy?
```

### Shell Access
```bash
docker exec -it metroa-backend bash        # Open shell in container
```

---

## 🔄 AFTER CODE UPDATES

```bash
cd /workspace/metroa-demo
git pull origin main
bash README/scripts/build-docker-runpod.sh  # Rebuild (30-45 min)
bash README/scripts/run-docker-runpod.sh    # Run new version
```

---

## 🆘 TROUBLESHOOTING

### Container won't start?
```bash
# Check Docker daemon
docker info

# If not running:
dockerd > /dev/null 2>&1 &
sleep 5
```

### Backend not responding?
```bash
docker logs metroa-backend --tail 100      # Check logs
docker restart metroa-backend              # Restart
```

### Need clean slate?
```bash
docker rm -f metroa-backend                # Remove container
docker system prune -f                     # Clean up Docker
bash README/scripts/run-docker-runpod.sh   # Start fresh
```

---

## 📚 FULL DOCUMENTATION

- Complete guide: `cat README/deployment/DOCKER_RUNPOD_COMPLETE.md`
- Build script details: `cat README/scripts/build-docker-runpod.sh`
- Run script details: `cat README/scripts/run-docker-runpod.sh`

---

## 🎯 THAT'S IT!

**Build once (30-45 min) → Run forever (10 sec)**

The Docker container includes:
- ✅ COLMAP 3.10 (GPU-accelerated)
- ✅ OpenMVS v2.2.0
- ✅ Open3D 0.19.0
- ✅ All Python dependencies

**No manual installation needed!**


