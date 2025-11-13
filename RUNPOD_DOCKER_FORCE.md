# Force Docker Build on RunPod

**Copy/paste this entire command:**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && pkill dockerd 2>/dev/null; rm -f /var/run/docker.sock /var/run/docker.pid 2>/dev/null; dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 > /tmp/dockerd.log 2>&1 & sleep 10 && docker build --tag metroa-backend:latest --file Dockerfile .
```

**If that fails, try this step-by-step:**

```bash
cd /workspace/metroa-demo && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && pkill dockerd 2>/dev/null; nohup dockerd > /tmp/dockerd.log 2>&1 & sleep 10 && docker info && docker build --tag metroa-backend:latest --file Dockerfile .
```

