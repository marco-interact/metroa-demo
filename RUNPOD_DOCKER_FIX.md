# RunPod Docker Fix

**The issue:** Docker daemon needs to be started as a service, not just backgrounded.

**Try this one-liner:**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && (curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh || true) && service docker start && sleep 3 && docker build --tag metroa-backend:latest --file Dockerfile .
```

**If that doesn't work, use this (builds directly without Docker):**

```bash
cd /workspace && git clone https://github.com/marco-interact/metroa-demo.git 2>/dev/null || (cd metroa-demo && git pull) && cd metroa-demo && bash setup-metroa-pod.sh
```

**The second option uses the existing setup script which builds COLMAP/OpenMVS directly without Docker.**

