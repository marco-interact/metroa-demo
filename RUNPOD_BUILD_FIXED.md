# RunPod Build - Fixed One-Liner

**Copy/paste this entire command on RunPod terminal:**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && systemctl start docker && systemctl enable docker && docker build --tag metroa-backend:latest --file Dockerfile .
```

**If systemctl doesn't work, use this alternative:**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && dockerd > /dev/null 2>&1 & sleep 5 && docker build --tag metroa-backend:latest --file Dockerfile .
```

