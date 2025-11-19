# 🔍 Troubleshoot Docker Push Failures

## 🧪 **Run These Diagnostic Commands**

```bash
# 1. Check if you're logged in
docker info | grep Username

# 2. Check if local image exists
docker images | grep metroa-backend

# 3. Try logging in again
docker logout
docker login
# Enter username: marcoaurelio
# Enter password: (your Docker Hub password)

# 4. Verify repository exists on Docker Hub
# Go to: https://hub.docker.com/u/marcoaurelio
# You should see "metroa-backend" listed

# 5. Try push again
docker tag metroa-backend:fast marcoaurelio/metroa-backend:latest
docker push marcoaurelio/metroa-backend:latest
```

---

## ⚠️ **Common Failure Reasons**

### **1. Repository Doesn't Exist**
**Error:** `denied: requested access to the resource is denied`

**Fix:**
1. Go to https://hub.docker.com/
2. Login as `marcoaurelio`
3. Click **Repositories**
4. Click **Create Repository**
5. Name: `metroa-backend`
6. Visibility: **Public**
7. Click **Create**

---

### **2. Not Logged In**
**Error:** `unauthorized: authentication required`

**Fix:**
```bash
docker logout
docker login
# Username: marcoaurelio
# Password: (your password)
```

---

### **3. Wrong Password**
**Error:** `Error response from daemon: Get https://registry-1.docker.io/v2/: unauthorized`

**Fix:**
- Make sure you're using Docker Hub password (not email password)
- Reset password at: https://hub.docker.com/reset-password

---

### **4. Account Doesn't Exist**
**Error:** `unauthorized: incorrect username or password`

**Fix:**
- Verify username at https://hub.docker.com/
- Create account if needed: https://hub.docker.com/signup

---

### **5. Network/Connection Issues**
**Error:** `Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: request canceled`

**Fix:**
```bash
# Check Docker is running
docker ps

# Restart Docker Desktop
# Mac: Click Docker icon → Restart

# Try again
docker push marcoaurelio/metroa-backend:latest
```

---

## 🔐 **Verify Docker Hub Setup**

### **Check 1: Account exists**
```bash
# Visit (replace with your username)
open https://hub.docker.com/u/marcoaurelio
```

Should show your profile. If not, create account.

### **Check 2: Repository exists**
```bash
# Visit (replace with your username)
open https://hub.docker.com/r/marcoaurelio/metroa-backend
```

Should show repository page. If "404", create repository.

### **Check 3: You're logged in locally**
```bash
docker info | grep Username
# Should show: Username: marcoaurelio
```

If not:
```bash
docker login
# Enter: marcoaurelio
# Enter: (your password)
```

---

## 🎯 **Step-by-Step Recovery**

```bash
# Step 1: Logout
docker logout

# Step 2: Login fresh
docker login
# Username: marcoaurelio
# Password: (your Docker Hub password)
# Should say: Login Succeeded

# Step 3: Verify image exists locally
docker images | grep metroa-backend
# Should show:
# metroa-backend   fast   ...

# Step 4: Tag image
docker tag metroa-backend:fast marcoaurelio/metroa-backend:latest

# Step 5: Check tag worked
docker images | grep marcoaurelio
# Should show:
# marcoaurelio/metroa-backend   latest   ...

# Step 6: Push
docker push marcoaurelio/metroa-backend:latest
```

---

## 📸 **Expected Success Output**

```
The push refers to repository [docker.io/marcoaurelio/metroa-backend]
5f70bf18a086: Pushing [==>                ] 123.4MB/2.5GB
a3ed95caeb02: Pushing [======>            ] 456.7MB/3.2GB
...
latest: digest: sha256:abcdef1234567890... size: 12345
```

---

## 🆘 **If Still Failing, Share This Info**

Run these and share the output:

```bash
# 1. Check login status
docker info | grep Username

# 2. Check local images
docker images | grep metroa

# 3. Try push and copy EXACT error
docker push marcoaurelio/metroa-backend:latest
```

Then share:
- Exact error message
- Output of commands above
- Did you create repository on Docker Hub? (yes/no)

---

## 🔄 **Alternative: Use GitHub Container Registry**

If Docker Hub keeps failing, try GitHub Container Registry:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Tag for GitHub
docker tag metroa-backend:fast ghcr.io/YOUR_GITHUB_USERNAME/metroa-backend:latest

# Push
docker push ghcr.io/YOUR_GITHUB_USERNAME/metroa-backend:latest
```

But Docker Hub is simpler for RunPod, so let's fix that first!

