# Firebase + Cloud Run - Quick Start 🚀

Deploy Knowledge RAG to Firebase + Cloud Run with generous free tier:
- **2M Cloud Run requests/month FREE**
- **10GB Firebase Hosting + 360MB/day transfer FREE**
- **Expected cost: $0-5/month** for low-moderate traffic

## Prerequisites

1. **Install Tools**
   ```powershell
   # gcloud CLI
   winget install Google.CloudSDK
   
   # Firebase CLI
   npm install -g firebase-tools
   # OR
   curl -sL https://firebase.tools | pwsh
   
   # Docker Desktop
   winget install Docker.DockerDesktop
   ```

2. **Create GCP Project**
   - Go to https://console.cloud.google.com
   - Create new project or select existing
   - Note your PROJECT_ID

3. **Login**
   ```powershell
   gcloud auth login
   firebase login
   ```

## 🎯 One-Command Deployment

```powershell
.\deploy-firebase.ps1 -ProjectId "your-gcp-project-id" -GitHubToken "your_github_token"
```

That's it! The script will:
- ✅ Enable required APIs
- ✅ Store secrets securely
- ✅ Build Docker container
- ✅ Deploy to Cloud Run
- ✅ Test endpoints
- ✅ Show you the live URL

## Manual Deployment (Step-by-Step)

### 1. Enable APIs & Store Secret

```powershell
$PROJECT_ID = "your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable services
gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com

# Store GitHub token
"your_github_token_here" | gcloud secrets create github-token --data-file=-
```

### 2. Build & Deploy

```powershell
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/knowledge-rag

# Deploy to Cloud Run
gcloud run deploy knowledge-rag `
  --image gcr.io/$PROJECT_ID/knowledge-rag `
  --region us-central1 `
  --allow-unauthenticated `
  --set-secrets GITHUB_TOKEN=github-token:latest `
  --memory 2Gi
```

### 3. Get URL & Test

```powershell
$URL = gcloud run services describe knowledge-rag --region us-central1 --format 'value(status.url)'
echo "Your API: $URL"

# Test
curl "$URL/api/stats"
```

## 🌐 Add Firebase Hosting (Optional)

Deploy a custom domain with global CDN:

```powershell
# Initialize Firebase
firebase init hosting

# Deploy
firebase deploy --only hosting
```

Your app will be live at: `https://your-project.web.app`

## 🔧 Configuration

### Environment Variables (Already Set)
- `GITHUB_TOKEN` - Stored in Secret Manager ✅
- `FLASK_ENV=production` ✅
- `LOG_LEVEL=INFO` ✅
- `CACHE_DIR=/app/cache` ✅

### Resource Limits (Tuned for Free Tier)
- Memory: 2GB
- CPU: 2 cores
- Timeout: 5 minutes
- Concurrency: 80 requests/instance
- Min instances: 0 (scales to zero = FREE when idle)
- Max instances: 10

## 📊 Monitoring

### View Logs
```powershell
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=knowledge-rag"
```

### Check Metrics (Console)
- Visit: https://console.cloud.google.com/run
- Click "knowledge-rag"
- See requests, latency, errors

## 🔄 Update Deployment

```powershell
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/knowledge-rag
gcloud run deploy knowledge-rag --image gcr.io/$PROJECT_ID/knowledge-rag
```

## 🤖 Auto-Deploy with GitHub Actions

1. **Configure Workload Identity** (one-time setup):
   ```powershell
   # See FIREBASE_DEPLOYMENT.md Step 7 for full commands
   ```

2. **Add GitHub Secrets**:
   - `GCP_PROJECT_ID`
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`
   - `GCP_SERVICE_ACCOUNT`

3. **Push to trigger deployment**:
   ```powershell
   git push origin main
   ```

GitHub Actions will automatically deploy! ✨

## 💰 Cost Breakdown

### Free Tier (Monthly)
- Cloud Run: 2M requests
- Cloud Storage: 5GB
- Secret Manager: 6 active versions
- Network egress: 1GB (North America)

### Paid (after free tier)
- Cloud Run: ~$0.40 per million requests
- Storage: ~$0.026/GB/month
- **Estimated total: $0-10/month** for most use cases

## 🔐 Security Checklist

- [x] Secrets in Secret Manager (not in code)
- [x] HTTPS automatic via Cloud Run
- [x] Rate limiting (10 req/min per IP)
- [x] Input validation (500 char max)
- [x] Security headers (CSP, HSTS, etc.)
- [x] No debug mode in production
- [ ] Enable GitHub secret scanning (manual)
- [ ] Enable Dependabot (manual)

## 🆘 Troubleshooting

**Build fails?**
```powershell
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

**Deployment fails?**
```powershell
gcloud run services describe knowledge-rag --region us-central1
```

**502/503 errors?**
- Check logs: `gcloud logging tail`
- Ensure Docker container starts properly
- Verify `GITHUB_TOKEN` secret is accessible

**Need help?**
- Full guide: `FIREBASE_DEPLOYMENT.md`
- Security: `SECURITY.md`

## 📚 Documentation

- **FIREBASE_DEPLOYMENT.md** - Complete Firebase + Cloud Run guide
- **SECURITY.md** - Security best practices
- **README.md** - Project overview

---

**Ready to deploy?** Run:
```powershell
.\deploy-firebase.ps1 -ProjectId "your-project-id" -GitHubToken "your_token"
```

🎉 You'll have a live API in ~5 minutes!
