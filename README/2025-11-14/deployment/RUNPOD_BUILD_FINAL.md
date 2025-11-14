# RunPod Docker Build - Final Command

**Dockerfile exists at root. Use this command:**

```bash
cd /workspace/metroa-demo && pkill dockerd 2>/dev/null; rm -f /var/run/docker.sock /var/run/docker.pid 2>/dev/null; nohup dockerd > /tmp/dockerd.log 2>&1 & sleep 10 && docker info && docker build --tag metroa-backend:latest --file Dockerfile .
```

**Check Docker daemon logs if it fails:**
```bash
tail -50 /tmp/dockerd.log
```

**Verify Dockerfile exists:**
```bash
ls -la /workspace/metroa-demo/Dockerfile
cat /workspace/metroa-demo/Dockerfile | head -5
```

