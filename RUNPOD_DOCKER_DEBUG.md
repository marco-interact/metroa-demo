# RunPod Docker Debug & Fix

**First, check why dockerd is failing:**

```bash
tail -50 /tmp/dockerd.log
```

**Common fixes:**

**Fix 1: Create required directories**
```bash
cd /workspace/metroa-demo && mkdir -p /var/lib/docker /var/run && dockerd --data-root=/var/lib/docker --pidfile=/var/run/docker.pid > /tmp/dockerd.log 2>&1 & sleep 15 && docker ps && docker build --tag metroa-backend:latest --file Dockerfile .
```

**Fix 2: Use different storage driver**
```bash
cd /workspace/metroa-demo && mkdir -p /var/lib/docker && dockerd --storage-driver=vfs --data-root=/var/lib/docker > /tmp/dockerd.log 2>&1 & sleep 15 && docker ps && docker build --tag metroa-backend:latest --file Dockerfile .
```

**Fix 3: Use rootless Docker**
```bash
cd /workspace/metroa-demo && dockerd-rootless-setuptool.sh install && export PATH=$HOME/bin:$PATH && dockerd-rootless.sh > /tmp/dockerd.log 2>&1 & sleep 15 && docker build --tag metroa-backend:latest --file Dockerfile .
```

**Fix 4: Skip Docker entirely - build directly (RECOMMENDED)**
```bash
cd /workspace/metroa-demo && bash setup-metroa-pod.sh
```

