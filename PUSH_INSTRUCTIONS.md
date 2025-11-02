# Push Instructions

## The Problem

Vercel is trying to build from GitHub `main` branch, but your latest changes (Node.js engine fix, OpenStreetMap) aren't pushed yet.

---

## Solution: Push to GitHub

You need to push from your Mac. The git push command needs authentication.

### Option 1: Push via Terminal

Open a new Terminal window (not this one) and run:

```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
git push origin main
```

### Option 2: Push via GitHub Desktop

If you have GitHub Desktop installed:
1. Open GitHub Desktop
2. Select the `colmap-demo` repository
3. Click "Push origin"

### Option 3: Use GitHub CLI

If you have `gh` installed:

```bash
cd /Users/marco.aurelio/Desktop/colmap-demo
gh auth login
git push origin main
```

---

## After Push

Vercel will automatically detect the new commit and redeploy.

Or trigger manual redeploy by running in this terminal:

```bash
./update-vercel-final.sh
```

---

## What Needs to be Pushed

- Node.js engine fix (>=18.x instead of 22.x)
- OpenStreetMap location picker
- Cleanup (60+ files removed)
- Updated dependencies (leaflet, react-leaflet)

---

**TLDR: Open a new terminal and run `git push origin main` from the project directory.**

