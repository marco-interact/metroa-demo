# Deployment Checklist - RunPod COLMAP Demo

## Pre-Deployment Checklist

### ✅ Repository Preparation

- [ ] All unnecessary files removed (venv, __pycache__, cache)
- [ ] `.gitignore` updated to exclude temporary files
- [ ] Cursor logs organized by date in `cursor-logs/` folder
- [ ] All code committed and pushed to GitHub
- [ ] README.md updated with latest information
- [ ] Environment variables documented

### ✅ GitHub Repository

- [ ] Repository URL: https://github.com/marco-interact/colmap-demo.git
- [ ] Repository is public or team has access
- [ ] All branches are up to date
- [ ] Latest commit includes deployment configurations

---

## RunPod Backend Deployment

### 📋 Pod Information

| Item | Value | Status |
|------|-------|--------|
| **Pod ID** | `xhqt6a1roo8mrc` | ⏳ Pending |
| **Pod Name** | colmap_worker_gpu | ⏳ Pending |
| **Storage Volume ID** | `rrtms4xkiz` | ⏳ Pending |
| **Storage Name** | colmap-gpu-volume | ⏳ Pending |

### 🚀 Deployment Steps

- [ ] **Step 1**: Access RunPod web terminal
- [ ] **Step 2**: Run automated setup script:
  ```bash
  cd /workspace
  git clone https://github.com/marco-interact/colmap-demo.git
  cd colmap-demo
  chmod +x runpod-setup.sh
  ./runpod-setup.sh
  ```
- [ ] **Step 3**: Verify COLMAP installation:
  ```bash
  colmap -h
  ```
- [ ] **Step 4**: Test GPU availability:
  ```bash
  nvidia-smi
  ```
- [ ] **Step 5**: Start backend server:
  ```bash
  /workspace/start-colmap.sh
  ```
- [ ] **Step 6**: Test health endpoint:
  ```bash
  curl http://localhost:8000/health
  ```
- [ ] **Step 7**: Verify public endpoint:
  ```
  http://xhqt6a1roo8mrc-8000.proxy.runpod.net
  ```

### ✅ Backend Verification

- [ ] Backend server is running
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Demo projects are accessible via `/api/projects`
- [ ] COLMAP binary is in PATH
- [ ] Database is initialized with demo data
- [ ] Storage directories exist and are writable

---

## Vercel Frontend Deployment

### 📋 Vercel Information

| Item | Value | Status |
|------|-------|--------|
| **Team** | interact-hq | ⏳ Pending |
| **Team ID** | `team_PWckdPO4Vl3C1PWOA9qs9DrI` | ⏳ Pending |
| **Project Name** | colmap-demo | ⏳ Pending |

### 🚀 Deployment Steps

- [ ] **Step 1**: Install Vercel CLI (if needed):
  ```bash
  npm install -g vercel
  ```
- [ ] **Step 2**: Navigate to project:
  ```bash
  cd /workspace/colmap-demo
  ```
- [ ] **Step 3**: Install dependencies:
  ```bash
  npm install
  ```
- [ ] **Step 4**: Build the application:
  ```bash
  npm run build
  ```
- [ ] **Step 5**: Deploy to Vercel:
  ```bash
  vercel --prod --scope interact-hq --yes
  ```
- [ ] **Step 6**: Set environment variable in Vercel:
  ```bash
  vercel env add NEXT_PUBLIC_API_URL production
  # Value: http://xhqt6a1roo8mrc-8000.proxy.runpod.net
  ```
- [ ] **Step 7**: Verify deployment URL (copy from Vercel output)

### ✅ Frontend Verification

- [ ] Vercel deployment successful
- [ ] Frontend is accessible at Vercel URL
- [ ] Environment variable `NEXT_PUBLIC_API_URL` is set correctly
- [ ] Frontend can connect to backend API
- [ ] Demo projects load correctly
- [ ] 3D viewer displays models
- [ ] Upload functionality works

---

## Integration Testing

### 🧪 End-to-End Tests

- [ ] **Test 1**: Load homepage
  - [ ] Navigate to Vercel URL
  - [ ] Verify UI loads correctly
  - [ ] Check for any console errors

- [ ] **Test 2**: View demo projects
  - [ ] Click on "Projects" or "Dashboard"
  - [ ] Verify demo scans appear
  - [ ] Click on a demo project
  - [ ] Verify 3D model loads

- [ ] **Test 3**: API connectivity
  - [ ] Open browser dev tools
  - [ ] Monitor network tab
  - [ ] Verify API calls to RunPod backend
  - [ ] Check for CORS errors

- [ ] **Test 4**: Upload functionality
  - [ ] Navigate to upload page
  - [ ] Try uploading test images
  - [ ] Verify upload progress
  - [ ] Check backend receives files

- [ ] **Test 5**: Processing workflow
  - [ ] Start a reconstruction job
  - [ ] Monitor processing status
  - [ ] Verify results are generated
  - [ ] Check 3D output

---

## Post-Deployment

### 📊 Monitoring

- [ ] Backend logs are accessible
- [ ] GPU usage is monitored via `nvidia-smi`
- [ ] Disk space is monitored via `df -h`
- [ ] Error logging is configured

### 🔒 Security

- [ ] CORS configured correctly
- [ ] File upload limits enforced
- [ ] API rate limiting considered
- [ ] SSL/HTTPS enabled (Vercel default)

### 📝 Documentation

- [ ] Deployment URLs documented
- [ ] API endpoints documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide created
- [ ] Team members notified

---

## Rollback Plan

If deployment fails:

### Backend Rollback

```bash
cd /workspace/colmap-demo
git log --oneline -5
git checkout <previous-commit-hash>
lsof -ti:8000 | xargs kill -9
/workspace/start-colmap.sh
```

### Frontend Rollback

```bash
# Via Vercel dashboard: Deployments → Previous deployment → Promote to Production
# Or via CLI:
vercel rollback <previous-deployment-url> --scope interact-hq
```

---

## Contact Information

### Support Resources

- **Documentation**: `/workspace/colmap-demo/cursor-logs/2025-11-03/`
- **Quick Reference**: `cursor-logs/2025-11-03/QUICK_REFERENCE.md`
- **Full Guide**: `cursor-logs/2025-11-03/RUNPOD_DEPLOYMENT_GUIDE.md`
- **GitHub Issues**: https://github.com/marco-interact/colmap-demo/issues

---

## Deployment Timeline

| Phase | Estimated Time | Actual Time | Status |
|-------|---------------|-------------|--------|
| Pre-deployment prep | 10 min | - | ⏳ Pending |
| Backend setup | 20 min | - | ⏳ Pending |
| COLMAP installation | 15 min | - | ⏳ Pending |
| Backend verification | 5 min | - | ⏳ Pending |
| Frontend build | 5 min | - | ⏳ Pending |
| Frontend deployment | 3 min | - | ⏳ Pending |
| Integration testing | 15 min | - | ⏳ Pending |
| **Total** | **~73 min** | - | ⏳ Pending |

---

## Success Criteria

✅ **Deployment is successful when:**

1. Backend health endpoint returns 200 OK
2. Frontend loads without errors
3. Demo projects are visible and accessible
4. 3D viewer displays models correctly
5. API calls from frontend to backend work
6. GPU is detected and available
7. COLMAP can process test images
8. Database queries return expected data

---

## Next Steps After Deployment

1. Monitor logs for first 24 hours
2. Test with real user uploads
3. Optimize processing parameters if needed
4. Set up automated backups
5. Configure alerting for errors
6. Document any issues encountered
7. Update team on deployment status

---

**Checklist Created**: 2025-11-03  
**Deployment Status**: Ready for deployment  
**Last Updated**: 2025-11-03

