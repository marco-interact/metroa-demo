# 🔧 Fix Existing Directory Issue

**When `metroa-demo` directory already exists**

---

## ✅ Option 1: Remove and Clone Fresh (Recommended)

```bash
cd /workspace
rm -rf metroa-demo
git clone https://github.com/marco-interact/metroa-demo.git
cd metroa-demo
bash setup-pod-8pexe48luksdw3.sh
```

---

## ✅ Option 2: Pull Latest Changes (If Already a Git Repo)

```bash
cd /workspace/metroa-demo
git fetch origin
git reset --hard origin/main
git pull origin main
bash setup-pod-8pexe48luksdw3.sh
```

---

## ✅ Option 3: One-Liner Force Replace

```bash
cd /workspace && rm -rf metroa-demo && git clone https://github.com/marco-interact/metroa-demo.git && cd metroa-demo && bash setup-pod-8pexe48luksdw3.sh
```

---

## ⚠️ Important Notes

- **Option 1** removes everything and starts fresh (safest)
- **Option 2** keeps existing files but updates code (faster)
- **Option 3** is the quickest one-liner

**If you have important data in `/workspace/metroa-demo`:**
- Check if data is on the volume (`/workspace/data/`) - it's safe
- Only code in `/workspace/metroa-demo/` will be replaced

---

**Recommended:** Use Option 1 or Option 3 for clean setup.

