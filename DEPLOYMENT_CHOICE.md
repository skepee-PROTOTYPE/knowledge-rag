# Knowledge RAG Deployment - Firebase Selected ✅

## Decision: Firebase + Cloud Run

**Why Firebase + Cloud Run?**
- ✅ **Free tier**: 2M requests/month, 5GB storage
- ✅ **Cost-effective**: $0-5/month for most use cases
- ✅ **Auto-scaling**: Scales to zero when idle (no cost)
- ✅ **Global CDN**: Firebase Hosting included
- ✅ **Easy setup**: One-command deployment

**vs Azure Web App:**
- ❌ Minimum ~$13/month (Basic B1 plan)
- ❌ Always-on pricing (even when idle)
- ❌ More complex setup

## 🚀 Deploy Now

```powershell
.\deploy-firebase.ps1 -ProjectId "your-gcp-project-id" -GitHubToken "your_github_token"
```

## Status

### ✅ Completed
- [x] Security hardening (rate limiting, validation, headers)
- [x] Production WSGI configuration
- [x] GitHub Actions CI pipeline
- [x] GitHub Actions deployment workflow (Cloud Run)
- [x] Firebase configuration (firebase.json)
- [x] Automated deployment script
- [x] Quick-start guide
- [x] Complete documentation

### 📋 To Do (Manual Steps)

1. **Deploy to Cloud Run**
   - Run `.\deploy-firebase.ps1` with your GCP project ID
   - Script handles everything automatically

2. **Enable GitHub Security** (2 minutes)
   - Go to repo Settings → Security → Code security
   - Enable: Secret scanning, Push protection, Dependabot

3. **Optional: Firebase Hosting** (5 minutes)
   ```powershell
   firebase init hosting
   firebase deploy --only hosting
   ```

4. **Optional: GitHub Actions Auto-Deploy** (10 minutes)
   - Follow `FIREBASE_DEPLOYMENT.md` Step 7
   - Configure workload identity and GitHub secrets
   - Push to main = automatic deployment

## Files Created

### Deployment
- `deploy-firebase.ps1` - One-command automated deployment
- `firebase.json` - Firebase Hosting configuration
- `Dockerfile` - Production container (already existed)
- `.github/workflows/deploy.yml` - Cloud Run auto-deploy
- `.github/workflows/ci.yml` - Continuous integration

### Documentation
- `QUICKSTART.md` - Quick start guide (this file)
- `FIREBASE_DEPLOYMENT.md` - Complete step-by-step guide
- `SECURITY.md` - Security policies and checklist

### Code
- `rate_limiter.py` - API rate limiting
- `wsgi_prod.py` - Production WSGI with security headers
- `app.py` - Updated with logging, validation, error handling

## Cost Estimate

**Free Tier Coverage:**
- 2M Cloud Run requests/month
- 5GB Cloud Storage
- 1GB network egress
- 6 Secret Manager versions

**Expected Monthly Cost:**
- Development: **$0** (within free tier)
- Low traffic (<100k requests): **$0-2**
- Moderate traffic (500k requests): **$2-5**
- High traffic (2M+ requests): **$10-20**

## Next Action

Run this command to deploy:

```powershell
.\deploy-firebase.ps1 -ProjectId "YOUR_PROJECT_ID" -GitHubToken "YOUR_GITHUB_TOKEN"
```

Get your PROJECT_ID from: https://console.cloud.google.com

---

Last updated: October 25, 2025
