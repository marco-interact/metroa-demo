# 🚨 Quick Fix Guide - Frontend API Errors

## Problem
Frontend showing 404/502 errors when connecting to backend API.

## Root Cause
`NEXT_PUBLIC_API_URL` environment variable is **NOT SET** in Vercel.

## Immediate Fix (5 minutes)

### Step 1: Get Your RunPod Backend URL
1. Go to [RunPod Console](https://www.runpod.io/console/pods)
2. Find your pod ID (e.g., `ngpxlcgh01a13s`)
3. Your backend URL format: `https://YOUR-POD-ID-8888.proxy.runpod.net`
   - Example: `https://ngpxlcgh01a13s-8888.proxy.runpod.net`

### Step 2: Verify Backend is Running
1. Open your backend URL in browser: `https://YOUR-POD-ID-8888.proxy.runpod.net/health`
2. Should return: `{"status":"healthy"}`
3. If not working:
   - Check RunPod pod is **Running**
   - Check pod logs: `tail -f /tmp/backend-startup.log`

### Step 3: Set Vercel Environment Variable
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select project: **metroa-demo**
3. **Settings** → **Environment Variables**
4. Click **Add New**
5. Set:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-POD-ID-8888.proxy.runpod.net`
   - **Environment**: ✅ Production ✅ Preview ✅ Development
6. Click **Save**

### Step 4: Redeploy
1. Go to **Deployments** tab
2. Click **⋯** on latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete (~2 minutes)

### Step 5: Test
1. Open your frontend: `https://metroa-demo.vercel.app`
2. Check browser console (F12) - should see:
   ```
   🔍 Using Next.js API proxy: /api/backend
   ```
3. Test health endpoint: `https://metroa-demo.vercel.app/api/backend/health`
   - Should return: `{"status":"healthy"}`

## Verification Checklist

- [ ] Backend accessible: `https://YOUR-POD-ID-8888.proxy.runpod.net/health`
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Vercel deployment completed
- [ ] Frontend can access `/api/backend/health`
- [ ] No more 404/502 errors in browser console

## If Still Not Working

### Check Backend Logs
```bash
# In RunPod Web Terminal
tail -f /tmp/backend-startup.log
```

### Check Vercel Build Logs
1. Go to Vercel → Deployments
2. Click on latest deployment
3. Check **Build Logs** for errors

### Test Backend Directly
```bash
# Test health
curl https://YOUR-POD-ID-8888.proxy.runpod.net/health

# Test projects
curl https://YOUR-POD-ID-8888.proxy.runpod.net/api/projects
```

### Common Issues

**Issue**: Backend returns 404
- **Fix**: Check backend URL includes `https://` and port `8888`

**Issue**: Backend returns 502
- **Fix**: Backend not running - check RunPod pod status and logs

**Issue**: CORS errors
- **Fix**: Backend already configured for CORS - check backend is running

**Issue**: Environment variable not taking effect
- **Fix**: Must redeploy Vercel app after setting env var

