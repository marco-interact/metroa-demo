# RunPod Build One-Liner

**Copy/paste this entire command on RunPod terminal:**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && docker build --tag metroa-backend:latest --file Dockerfile .
```

**What it does:**
1. Clones repo (or pulls if exists)
2. Installs Docker
3. Builds the image

**Time:** ~30-45 minutes

