# 🚀 Deploy Advanced FPS Viewer

## ✅ What Was Updated

### New Features
1. **Collision Detection** - Octree-based spatial partitioning
2. **Smooth Physics** - Acceleration/deceleration system
3. **Design Tokens** - Consistent Tailwind styling
4. **10M+ Optimization** - Auto-downsampling for large clouds

### Files Changed
- ✅ `src/components/3d/FirstPersonViewer.tsx` - Enhanced with all features
- ✅ `src/utils/octree.ts` - New octree implementation
- ✅ `FPS_VIEWER_ADVANCED.md` - Comprehensive documentation

---

## 📦 Deployment Commands

### 1️⃣ Already Pushed to GitHub ✅

```bash
# Already completed:
git add -A
git commit -m "feat: Advanced FPS Viewer..."
git push origin main
```

**Status**: ✅ Pushed successfully to `marco-interact/metroa-demo`

---

### 2️⃣ Deploy Frontend to Vercel

From your Mac terminal:

```bash
cd /Users/marco.aurelio/Desktop/metroa-demo
npx vercel --prod
```

**Expected Output**:
```
🔍 Inspect: https://vercel.com/...
✅ Production: https://metroa-demo.vercel.app
```

**Build Time**: ~2-3 minutes

---

### 3️⃣ Pull Changes on RunPod

**SSH into RunPod** (from Mac terminal):
```bash
ssh root@203.57.40.132 -p 10164 -i ~/.ssh/id_ed25519
```

**Once connected, pull latest changes**:
```bash
cd /workspace/metroa-demo
git pull origin main
```

**Expected Output**:
```
From https://github.com/marco-interact/metroa-demo
   48c930f..1a234d8  main       -> origin/main
Updating 48c930f..1a234d8
Fast-forward
 FPS_VIEWER_ADVANCED.md                      | 456 ++++++++++++
 src/components/3d/FirstPersonViewer.tsx     | 841 +++++++++++++--------
 src/utils/octree.ts                         | 338 ++++++++
 3 files changed, 1135 insertions(+), 294 deletions(-)
```

**Note**: Backend code hasn't changed, no need to restart backend.

---

## 🧪 Testing

### Frontend Test (After Vercel Deploy)

1. **Visit**: https://metroa-demo.vercel.app
2. **Navigate to**: Any scan with point cloud
3. **Switch to**: "First Person" mode
4. **Verify**:
   - ✅ Crosshair appears
   - ✅ WASD movement is smooth (not instant start/stop)
   - ✅ UI uses blue accent colors (#3E93C9)
   - ✅ Position HUD shows coordinates
   - ✅ Octree badge appears (green text with node count)
   - ✅ Point count badge shows "X.XM"

### Collision Detection Test

1. **Walk toward a wall** in the point cloud
2. **Expected**: Camera stops smoothly before passing through
3. **Try strafing along wall**: Should slide smoothly
4. **Check console**: Should see octree build message:
   ```
   🌳 Building octree for collision detection...
   ✅ Octree built in 243ms
      - Nodes: 4,523
      - Points: 2,450,000
      - Max Depth: 7
   ```

### Large Point Cloud Test

1. **Upload a 10M+ point video/scan**
2. **Check console** for downsampling:
   ```
   ⚡ Large point cloud detected (12.4M points), applying downsampling...
   ✅ Downsampled to 4.1M points
   ```
3. **Verify**: Should maintain 60 FPS in FPS mode

### Smooth Movement Test

1. **Press W** and observe acceleration (not instant speed)
2. **Release W** and observe deceleration (smooth stop)
3. **Sprint test**: Hold Shift + W, should smoothly ramp to 2× speed
4. **Strafe test**: A/D should also be smooth

---

## 🎨 Visual Changes to Verify

### Before vs After

**Old UI**:
- Generic gray backgrounds
- Inconsistent button styles
- Sharp movement
- Could walk through walls

**New UI**:
- Dark elevated surfaces with backdrop blur
- Blue accent borders (#3E93C9)
- Smooth physics
- Collision detection active
- Octree stats visible

### Key Visual Elements

1. **Top Bar Buttons**:
   - Background: `bg-surface-elevated/90`
   - Border: `border-app-primary`
   - Hover: `hover:border-primary-400`

2. **Position HUD** (bottom-left):
   - Blue icon and header
   - Clean tabular numbers
   - Glass morphism effect

3. **Octree Stats Badge** (top bar):
   - Green text for octree nodes
   - Shows collision is active

4. **Controls Help Panel**:
   - Rounded corners
   - Consistent spacing
   - Mentions collision detection at bottom

---

## 🐛 Troubleshooting

### Issue: No Octree Badge Appears

**Cause**: Octree failed to build
**Check**:
```javascript
// Open browser console
// Look for error message after point cloud loads
```
**Fix**: Point cloud may be too sparse or corrupted

---

### Issue: Movement Feels Too Slow/Fast

**Solution**: Adjust speed slider (bottom-right)
- Range: 0.5 - 10.0
- Default: 3.0
- Recommended for collision: 2.0 - 4.0

---

### Issue: Collision Too Sensitive

**Temporary**: Disable collision by checking octree build
**Long-term**: Adjust `collisionRadius` in code (default: 0.3)

---

### Issue: Vercel Build Fails

**Check**:
```bash
# Test build locally
npm run build
```

**Common Issues**:
- TypeScript errors
- Missing dependencies
- Import path errors

**Solution**:
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

---

## 📊 Performance Benchmarks

### Expected Performance

| Point Count | Build Time | Render FPS | Collision Speed |
|-------------|------------|------------|-----------------|
| 1M | 100ms | 60 | <1ms |
| 5M | 400ms | 60 | <1ms |
| 10M | 600ms* | 60 | 1-2ms |
| 15M+ | 800ms* | 60 | <1ms* |

*With automatic downsampling

---

## 🎯 Success Criteria

Your deployment is successful if:

- ✅ Vercel build completes without errors
- ✅ FPS mode loads and displays point cloud
- ✅ Movement has smooth acceleration (not instant)
- ✅ UI matches design system (blue accents, dark surfaces)
- ✅ Octree badge appears in top bar
- ✅ Collision prevents walking through geometry
- ✅ Performance is 60 FPS with 5M points
- ✅ Console shows octree build success
- ✅ No TypeScript/React errors in console

---

## 📝 Deployment Checklist

- [x] Code committed to Git
- [x] Pushed to GitHub (`marco-interact/metroa-demo`)
- [ ] Deployed to Vercel
- [ ] Pulled on RunPod (optional, frontend-only changes)
- [ ] Tested collision detection
- [ ] Tested smooth movement
- [ ] Verified UI styling
- [ ] Tested with large point cloud (5M+)
- [ ] Checked browser console for octree build
- [ ] Verified 60 FPS performance

---

## 🎉 Next Steps

After successful deployment:

1. **Test with real user scans** - Verify collision works with various geometries
2. **Monitor performance** - Check Vercel analytics for any issues
3. **Gather feedback** - Note any collision tuning needed
4. **Consider enhancements**:
   - Mesh reconstruction for better collision
   - LOD system for even larger clouds
   - GPU-based collision for ultimate performance

---

## 🆘 Need Help?

**Check Logs**:
- Vercel: Project Settings → Deployments → View Logs
- Browser: DevTools → Console
- RunPod: SSH in and check `docker logs`

**Common Commands**:
```bash
# Check Vercel deployment status
npx vercel ls

# Rollback if needed
npx vercel rollback

# Check Git status
git status
git log --oneline -5
```

---

## 📞 Support

If issues persist:
1. Check `FPS_VIEWER_ADVANCED.md` for detailed feature docs
2. Review browser console for errors
3. Test with a smaller point cloud first (< 1M points)
4. Verify TypeScript compilation: `npm run type-check`

---

**Deployment Date**: November 18, 2025
**Version**: Advanced FPS Viewer v2.0
**Commit**: `1a234d8`

