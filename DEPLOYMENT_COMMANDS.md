# Deployment Commands

## GitHub Push (Already Done ✅)

Latest commit: `5cba2d66` - FEAT: Integrate Spline animation loader for all loading states

## RunPod: Pull Latest Code

### Quick One-Liner

```bash
cd /workspace/metroa-demo && git pull origin main && echo "✅ Code updated"
```

### Full Update with Backend Restart

```bash
cd /workspace/metroa-demo && \
git pull origin main && \
lsof -ti :8888 | xargs kill -9 2>/dev/null || true && \
sleep 2 && \
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py" && \
sleep 3 && \
curl http://localhost:8888/health && \
echo "✅ Backend restarted"
```

### Step-by-Step

```bash
# 1. Navigate to project
cd /workspace/metroa-demo

# 2. Pull latest code
git pull origin main

# 3. Verify update
git log --oneline -1

# 4. (Optional) Restart backend if needed
lsof -ti :8888 | xargs kill -9 2>/dev/null
sleep 2
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py"
```

## Mac Terminal: Vercel Build

### Prerequisites

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel (if not already logged in)
vercel login
```

### Link Project (First Time Only)

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
vercel link
```

### Deploy to Production

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Option 1: Deploy with prompts
vercel --prod

# Option 2: Deploy without prompts (if already linked)
vercel --prod --yes

# Option 3: Deploy specific environment
vercel --prod --env NEXT_PUBLIC_BACKEND_URL=https://your-runpod-url.com
```

### Quick Deploy One-Liner

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo && vercel --prod --yes
```

### Build Locally (Test Before Deploy)

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Install dependencies (if needed)
npm install

# Build locally
npm run build

# Test production build locally
npm start
```

### Check Deployment Status

```bash
# List deployments
vercel ls

# View deployment logs
vercel logs

# View specific deployment
vercel inspect [deployment-url]
```

## Complete Deployment Workflow

### 1. RunPod (Backend)

```bash
ssh root@your-runpod-ip -p PORT -i ~/.ssh/id_ed25519

# Once connected:
cd /workspace/metroa-demo && \
git pull origin main && \
lsof -ti :8888 | xargs kill -9 2>/dev/null || true && \
sleep 2 && \
screen -S metroa-backend -d -m bash -c "cd /workspace/metroa-demo && python main.py" && \
sleep 3 && \
curl http://localhost:8888/health
```

### 2. Mac Terminal (Frontend)

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
vercel --prod --yes
```

## Verify Deployment

### Check Backend

```bash
# From RunPod terminal
curl http://localhost:8888/health
curl http://localhost:8888/api/status
```

### Check Frontend

Visit your Vercel deployment URL (usually shown after `vercel --prod`)

## Troubleshooting

### Backend Not Updating

```bash
# Force pull
cd /workspace/metroa-demo
git fetch origin
git reset --hard origin/main
```

### Vercel Build Fails

```bash
# Check build logs
vercel logs

# Build locally to see errors
npm run build

# Check for TypeScript errors
npx tsc --noEmit
```

### Backend Connection Issues

```bash
# Update frontend backend URL in Vercel
vercel env add NEXT_PUBLIC_BACKEND_URL production
# Enter: https://your-runpod-url.com
```

