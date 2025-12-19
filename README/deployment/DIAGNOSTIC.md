# Backend Connection Diagnostic Guide

## Issue Summary
Frontend is getting 404/502 errors when connecting to backend API.

## Root Causes
1. **Missing Environment Variable**: `NEXT_PUBLIC_API_URL` not set in Vercel
2. **Backend Not Running**: RunPod pod may be stopped or backend service not started
3. **Incorrect URL Format**: Backend URL must include protocol and port

## Step-by-Step Fix

### Step 1: Verify RunPod Backend is Running

1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. Check your pod status - should be **Running**
3. Click on your pod → **Connect** → **Web Terminal**
4. Run these commands:

```bash
# Check if backend is running
ps aux | grep python

# Check if port 8888 is listening
netstat -tlnp | grep 8888

# Check backend logs
tail -f /tmp/backend-startup.log

# If backend is not running, start it manually:
cd /app && python3 main.py
```

### Step 2: Get Your RunPod Backend URL

Your backend URL format should be:
```
https://YOUR-POD-ID-8888.proxy.runpod.net
```

Example:
```
https://ngpxlcgh01a13s-8888.proxy.runpod.net
```

**Important**: 
- Must include `https://` protocol
- Must include port `8888` in the subdomain
- No trailing slash

### Step 3: Set Vercel Environment Variable

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `metroa-demo`
3. Go to **Settings** → **Environment Variables**
4. Add/Update:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-POD-ID-8888.proxy.runpod.net`
   - **Environment**: Production, Preview, Development (select all)
5. **Save**
6. **Redeploy** your application (go to Deployments → Redeploy)

### Step 4: Test Backend Connectivity

After setting the environment variable, test:

1. **Health Check**:
   ```
   https://YOUR-POD-ID-8888.proxy.runpod.net/health
   ```
   Should return: `{"status":"healthy"}`

2. **Projects Endpoint**:
   ```
   https://YOUR-POD-ID-8888.proxy.runpod.net/api/projects
   ```
   Should return: `{"projects":[]}` or list of projects

3. **Frontend Proxy** (after redeploy):
   ```
   https://metroa-demo.vercel.app/api/backend/health
   ```
   Should proxy to backend and return health status

### Step 5: Verify Next.js Rewrites

The `next.config.js` should proxy:
- `/api/backend/*` → `${NEXT_PUBLIC_API_URL}/api/*`
- `/api/backend/health` → `${NEXT_PUBLIC_API_URL}/health`

Check Vercel build logs to see if rewrites are configured correctly.

## Common Issues & Solutions

### Issue: 404 Not Found
**Cause**: Backend URL not set or incorrect
**Solution**: Set `NEXT_PUBLIC_API_URL` in Vercel and redeploy

### Issue: 502 Bad Gateway
**Cause**: Backend not running or unreachable
**Solution**: 
1. Check RunPod pod is running
2. Check backend service is started
3. Verify backend URL is accessible from browser

### Issue: CORS Errors
**Cause**: Backend CORS not configured (should already be set to allow all)
**Solution**: Backend already has `allow_origins=["*"]` in `main.py`

### Issue: Timeout Errors
**Cause**: Backend taking too long to respond
**Solution**: Check backend logs for processing errors

## Verification Checklist

- [ ] RunPod pod is **Running**
- [ ] Backend service is started (check logs)
- [ ] Backend URL accessible: `https://YOUR-POD-ID-8888.proxy.runpod.net/health`
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Vercel deployment completed after env var change
- [ ] Frontend can access `/api/backend/health`

## Quick Test Commands

```bash
# Test backend directly
curl https://YOUR-POD-ID-8888.proxy.runpod.net/health

# Test backend projects endpoint
curl https://YOUR-POD-ID-8888.proxy.runpod.net/api/projects

# Test frontend proxy (after redeploy)
curl https://metroa-demo.vercel.app/api/backend/health
```

