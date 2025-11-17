# 🚀 Vercel Deployment Commands

## Quick Deploy (Mac Terminal)

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Set backend URL
echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production

# Deploy to production
vercel --prod
```

---

## Full Deployment Steps

### Step 1: Navigate to Project

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
```

### Step 2: Check/Create Environment Variables

```bash
# Create .env.production with backend URL
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"
EOF

# Verify it was created
cat .env.production
```

### Step 3: Deploy to Vercel

```bash
# Production deployment
vercel --prod
```

**Expected Output:**
```
Vercel CLI 33.0.0
🔍  Inspect: https://vercel.com/interact-hq/metroa-demo/...
✅  Production: https://metroa-demo.vercel.app [deployed]
```

---

## Alternative: Development Preview

```bash
# Deploy preview (not production)
vercel

# This creates a preview URL like:
# https://metroa-demo-git-main-interact-hq.vercel.app
```

---

## Vercel CLI Installation (if needed)

```bash
# Install Vercel CLI globally
npm install -g vercel

# Or use npx (no installation needed)
npx vercel --prod
```

---

## First Time Setup (if never deployed before)

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo

# Login to Vercel
vercel login

# Link to existing project (if already created)
vercel link

# Or let Vercel create new project
vercel --prod
# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? interact-hq
# - Link to existing project? Yes (if exists) or No
# - Project name? metroa-demo
# - Directory? ./
# - Override settings? No
```

---

## Environment Variables in Vercel Dashboard

If you want to set env vars in Vercel dashboard instead:

1. Go to: https://vercel.com/interact-hq/metroa-demo
2. Click **Settings** → **Environment Variables**
3. Add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://k0r2cn19yf6osw-8888.proxy.runpod.net`
   - **Environment**: Production ✓
4. Click **Save**
5. Redeploy:

```bash
vercel --prod --force
```

---

## Useful Vercel Commands

```bash
# Deploy to production
vercel --prod

# Force redeploy (ignore cache)
vercel --prod --force

# View deployments
vercel ls

# View logs
vercel logs

# Open project in browser
vercel --prod --open

# Check current project info
vercel project ls

# Remove deployment
vercel remove metroa-demo
```

---

## Build Configuration

Vercel automatically detects Next.js and uses these settings:

**Build Command:** `npm run build` or `next build`  
**Output Directory:** `.next`  
**Install Command:** `npm install`  
**Node Version:** 18.x (from package.json)

---

## Vercel Build Settings (vercel.json)

Already configured in `vercel.json`:

```json
{
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/backend/:path*",
      "destination": "https://k0r2cn19yf6osw-8888.proxy.runpod.net/api/:path*"
    }
  ]
}
```

---

## Troubleshooting

### Build Fails

```bash
# Check for errors locally first
npm run build

# If it builds locally, try force deploy
vercel --prod --force
```

### Environment Variables Not Working

```bash
# Make sure .env.production exists
cat .env.production

# Or set in Vercel dashboard and redeploy
vercel --prod --force
```

### Backend URL Wrong

```bash
# Update .env.production
echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production

# Redeploy
vercel --prod
```

### TypeScript Errors

TypeScript errors are ignored during build (configured in `next.config.js`):

```javascript
typescript: {
  ignoreBuildErrors: true,
}
```

### "Project not found"

```bash
# Relink to project
vercel link

# Or create new deployment
vercel --prod
```

---

## Post-Deployment Verification

### Test Frontend

```bash
# Open in browser
open https://metroa-demo.vercel.app

# Or test API connection
curl https://metroa-demo.vercel.app/api/backend/health
```

### Check Deployment Status

```bash
# View recent deployments
vercel ls

# View logs for specific deployment
vercel logs <deployment-url>
```

---

## Quick Deploy Checklist

- [ ] Navigate to project: `cd /Users/marco.aurelio/Desktop/metroa-demo`
- [ ] Set backend URL: `echo 'NEXT_PUBLIC_API_URL="..."' > .env.production`
- [ ] Deploy: `vercel --prod`
- [ ] Wait for build (~2-3 minutes)
- [ ] Test: `open https://metroa-demo.vercel.app`
- [ ] Verify backend connection (should not show 404 errors)

---

## Current Project Info

- **Project Name**: metroa-demo
- **Team/Scope**: interact-hq
- **Production URL**: https://metroa-demo.vercel.app
- **Backend URL**: https://k0r2cn19yf6osw-8888.proxy.runpod.net
- **Git Repository**: https://github.com/marco-interact/metroa-demo

---

## One-Line Deploy

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo && echo 'NEXT_PUBLIC_API_URL="https://k0r2cn19yf6osw-8888.proxy.runpod.net"' > .env.production && vercel --prod
```

---

**Deployment typically takes 2-3 minutes.**

After deployment, verify:
1. Frontend loads: https://metroa-demo.vercel.app
2. No 404 errors (backend must be running)
3. Can upload videos and start reconstructions

