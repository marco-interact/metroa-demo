# Fix Git Remote on RunPod

## Problem
```
fatal: 'metroa' does not appear to be a git repository
```

## Solution

### Step 1: Check Current Remotes
```bash
cd /workspace/metroa-demo
git remote -v
```

### Step 2: Add/Update Remote

#### Option A: If no remotes exist, add origin
```bash
git remote add origin https://github.com/marco-interact/metroa-demo.git
git remote -v
```

#### Option B: If origin exists but named differently, rename it
```bash
# Check current remotes
git remote -v

# If you see 'origin' pointing to wrong repo, update it:
git remote set-url origin https://github.com/marco-interact/metroa-demo.git

# Or if you want to keep both:
git remote add metroa https://github.com/marco-interact/metroa-demo.git
```

#### Option C: Use origin instead of metroa
```bash
# Just use origin (most common)
git pull origin main
```

### Step 3: Pull Latest Code
```bash
# Using origin
git pull origin main

# Or if you added metroa remote
git pull metroa main
```

### Step 4: Set Upstream (Optional)
```bash
# Set upstream branch
git branch --set-upstream-to=origin/main main

# Now you can just use:
git pull
```

## Complete Fix Script

```bash
cd /workspace/metroa-demo

# Check current remotes
git remote -v

# Add/update origin remote
git remote set-url origin https://github.com/marco-interact/metroa-demo.git

# Verify
git remote -v

# Pull latest code
git pull origin main

# Set upstream for future
git branch --set-upstream-to=origin/main main
```

## Quick One-Liner

```bash
cd /workspace/metroa-demo && git remote set-url origin https://github.com/marco-interact/metroa-demo.git && git pull origin main
```

