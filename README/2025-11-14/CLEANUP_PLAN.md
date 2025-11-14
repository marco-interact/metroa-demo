# Repository Cleanup Plan for Metroa-Demo

## Files to DELETE (Deprecated/Unused)

### Old Deployment Scripts (Obsolete)
- build-colmap-gpu.sh (replaced by build-colmap-gpu-fixed.sh)
- runpod-setup.sh (will be replaced by master script)
- runpod-install-colmap.sh (consolidated)
- runpod-diagnostic-and-fix.sh (consolidated)
- runpod-gpu-fix.sh (consolidated)
- deploy-frontend.sh (replaced)
- resume-runpod.sh (replaced by master script)
- install-colmap-service.sh (obsolete)
- install-supervisor.sh (obsolete)
- start-colmap-persistent.sh (obsolete)

### Documentation (Outdated/Duplicate)
- cursor-logs/ (entire directory - development logs)
- CICD_RESUME_GUIDE.md (obsolete)
- DEPLOYMENT_CHECKLIST.md (obsolete)
- DEPLOYMENT_INSTRUCTIONS.md (obsolete)
- DEPLOYMENT_QUICKSTART.md (obsolete)
- DEPLOYMENT_READY.md (obsolete)
- README_DEPLOYMENT.md (obsolete)

### Diagnostic Scripts (Consolidated)
- diagnose-gpu.sh (will consolidate into master script)
- scripts/diagnostics/ (entire directory)
- scripts/test/ (entire directory)

### Config Files (Unused)
- config/ (entire directory)
- Dockerfile (not using Docker, using native RunPod)

### Other
- .env.production (will regenerate for new pod)

## Files to KEEP (Active Stack)

### Core Backend
- main.py ✅
- database.py ✅
- colmap_processor.py ✅
- colmap_binary_parser.py ✅
- thumbnail_generator.py ✅
- requirements.txt ✅ (cleaned)

### Frontend (Next.js)
- src/ ✅ (entire directory)
- public/ ✅
- package.json ✅
- package-lock.json ✅
- next.config.js ✅
- tailwind.config.ts ✅
- tsconfig.json ✅
- postcss.config.js ✅
- next-env.d.ts ✅
- vercel.json ✅

### Data & Resources
- demo-resources/ ✅
- data/ ✅ (structure only)

### New Setup Scripts (To Create)
- setup-metroa-pod.sh ✅ (master setup)
- README.md ✅ (updated)

## Actions

1. Delete deprecated files
2. Clean requirements.txt (remove open3d)
3. Create master setup script
4. Update all environment variables
5. Create clean README
6. Push to new repo

