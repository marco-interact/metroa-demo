# RunPod Docker Build - Root User

**You're root, so ignore the warnings. Use this:**

```bash
cd /workspace/metroa-demo && pkill -9 dockerd 2>/dev/null; rm -rf /var/run/docker.sock /var/run/docker.pid /var/lib/docker/tmp 2>/dev/null; dockerd > /tmp/dockerd.log 2>&1 & sleep 15 && docker ps && docker build --tag metroa-backend:latest --file Dockerfile .
```

**If dockerd keeps failing, check logs:**
```bash
tail -100 /tmp/dockerd.log
```

**Alternative: Use rootless Docker (if above doesn't work):**
```bash
cd /workspace/metroa-demo && dockerd-rootless-setuptool.sh install && export PATH=$HOME/bin:$PATH && dockerd-rootless.sh > /tmp/dockerd.log 2>&1 & sleep 15 && docker build --tag metroa-backend:latest --file Dockerfile .
```

