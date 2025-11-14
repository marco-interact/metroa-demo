# RunPod Docker Build - Skip Install

**Docker is already installed. Use this command:**

```bash
cd /workspace/metroa-demo && pkill dockerd 2>/dev/null; rm -f /var/run/docker.sock /var/run/docker.pid 2>/dev/null; nohup dockerd > /tmp/dockerd.log 2>&1 & sleep 10 && docker info && docker build --tag metroa-backend:latest --file Dockerfile .
```

**Or if you want to check Docker status first:**

```bash
cd /workspace/metroa-demo && docker info 2>&1 || (pkill dockerd 2>/dev/null; rm -f /var/run/docker.sock /var/run/docker.pid 2>/dev/null; nohup dockerd > /tmp/dockerd.log 2>&1 & sleep 10) && docker build --tag metroa-backend:latest --file Dockerfile .
```

