# New RunPod Configuration

**Date:** December 19, 2025  
**Pod ID:** `b210isbvqbqqf1`  
**Backend URL:** `https://b210isbvqbqqf1-8888.proxy.runpod.net`

---

## 🚀 Quick Setup

### 1. Vercel Environment Variable

Go to: https://vercel.com/interact-hq/metroa-demo/settings/environment-variables

**Update:**
```
Name:  API_URL
Value: https://b210isbvqbqqf1-8888.proxy.runpod.net
```

**Then redeploy:**
```bash
vercel --prod
```

---

## 2. Local Development (.env.local)

Create or update `.env.local`:
```bash
API_URL=https://b210isbvqbqqf1-8888.proxy.runpod.net
NEXT_PUBLIC_API_URL=https://b210isbvqbqqf1-8888.proxy.runpod.net
```

---

## 3. Verify Backend Health

```bash
curl https://b210isbvqbqqf1-8888.proxy.runpod.net/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "...",
  "colmap_available": true,
  "openmvs_available": true
}
```

---

## 4. Test Full Pipeline

1. **Frontend:** https://metroa-demo-dpfzgd00g-interact-hq.vercel.app
2. **Login** to dashboard
3. **Create project**
4. **Upload video** (standard or 360°)
5. **Select quality:** Fast / High Quality / Ultra
6. **Monitor processing** (should be 50% faster with new optimizations)

---

## 📊 Expected Performance

| Quality Mode | Processing Time | Point Count |
|--------------|----------------|-------------|
| **Fast** | 2-4 minutes | 5M-15M points |
| **High Quality** | 4-7 minutes | 15M-40M points |
| **Ultra (OpenMVS)** | 5-12 minutes | 50M-150M+ points |

---

## ✅ New Pod Features

This pod has the optimized backend with:
- ✅ **50% faster** processing (optimized quality presets)
- ✅ **360° video support** (fixed imports)
- ✅ **No Open3D** (preserves 100% point cloud density)
- ✅ **Native FPS detection** (auto-detects 24/30 fps)
- ✅ **Multi-view extraction** (8 views per frame)
- ✅ **OpenMVS densification** (maximum quality)

---

## 🔧 Pod Configuration

**Docker Image:** `macoaurelio/metroa-backend:latest`  
**SHA:** `ab36a185619d73c5f197dd6078e55d95d8e9a33de9ad70d84b96414d162f7d30`  
**Port:** 8888  
**GPU:** Required for COLMAP/OpenMVS  

---

## 📝 Previous Pod (Deprecated)

**Old Pod ID:** `9doems3qzzhna3`  
**Old URL:** `https://9doems3qzzhna3-8888.proxy.runpod.net`  
**Status:** ❌ Replaced by new pod

---

## 🚨 Important Notes

1. **Always update Vercel env var** when changing pods
2. **Redeploy frontend** after env var change
3. **Test health endpoint** before uploading videos
4. **Monitor logs** in RunPod console for errors
5. **360° videos** require 2:1 aspect ratio (auto-detected)

---

## ✨ Quick Test Commands

```bash
# Test health
curl https://b210isbvqbqqf1-8888.proxy.runpod.net/health

# Test via Vercel proxy
curl https://metroa-demo-dpfzgd00g-interact-hq.vercel.app/api/backend/health

# Redeploy frontend
cd /Users/marco.aurelio/Desktop/metroa-demo
vercel --prod
```

---

**Pod Status:** ✅ Active  
**Backend:** ✅ Optimized & Ready  
**Frontend:** ⏳ Needs redeploy with new env var

