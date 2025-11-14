# 🔧 Fix Git Remote on RunPod

**When git remote 'metroa' doesn't exist**

---

## Step 1: Check Current Remotes

**On RunPod terminal:**

```bash
cd /workspace/metroa-demo
git remote -v
```

---

## Step 2: Add Correct Remote

**If no remotes exist or wrong remote:**

```bash
cd /workspace/metroa-demo

# Remove any incorrect remotes
git remote remove origin 2>/dev/null || true
git remote remove metroa 2>/dev/null || true

# Add correct remote
git remote add origin https://github.com/marco-interact/metroa-demo.git

# Verify
git remote -v
```

---

## Step 3: Pull Latest Code

```bash
cd /workspace/metroa-demo
git pull origin main
```

---

## One-Liner: Fix and Pull

**Copy/paste this:**

```bash
cd /workspace/metroa-demo && git remote remove origin 2>/dev/null || true && git remote add origin https://github.com/marco-interact/metroa-demo.git && git pull origin main
```

---

## Alternative: Use Direct URL

**If remote still doesn't work:**

```bash
cd /workspace/metroa-demo
git pull https://github.com/marco-interact/metroa-demo.git main
```

---

## Verify Remote is Correct

```bash
git remote -v
```

Should show:
```
origin  https://github.com/marco-interact/metroa-demo.git (fetch)
origin  https://github.com/marco-interact/metroa-demo.git (push)
```

