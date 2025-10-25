# Quick Deploy to Firebase + Cloud Run
# This script automates the deployment process

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$Region = "us-central1",
    [string]$ServiceName = "knowledge-rag"
)

Write-Host "==> Knowledge RAG - Firebase + Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[CHECK] Checking prerequisites..." -ForegroundColor Yellow
$gcloudExists = Get-Command gcloud -ErrorAction SilentlyContinue
$dockerExists = Get-Command docker -ErrorAction SilentlyContinue

if (-not $gcloudExists) {
    Write-Host "[ERROR] gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

if (-not $dockerExists) {
    Write-Host "[ERROR] Docker not found. Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Prerequisites satisfied" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "[SETUP] Setting GCP project to $ProjectId..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "[SETUP] Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable firebase.googleapis.com --quiet

# Store secret
Write-Host "[SECRETS] Storing GitHub token in Secret Manager..." -ForegroundColor Yellow
$secretExists = gcloud secrets list --filter="name:github-token" --format="value(name)" 2>$null
if ($secretExists) {
    Write-Host "   Secret already exists, creating new version..." -ForegroundColor Gray
    $GitHubToken | gcloud secrets versions add github-token --data-file=- 2>$null
} else {
    Write-Host "   Creating new secret..." -ForegroundColor Gray
    $GitHubToken | gcloud secrets create github-token --data-file=- 2>$null
}

# Grant Cloud Run access to secret
Write-Host "[SECRETS] Granting Cloud Run access to secrets..." -ForegroundColor Yellow
$projectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)"
gcloud secrets add-iam-policy-binding github-token `
    --member="serviceAccount:${projectNumber}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet 2>$null

# Build and deploy
Write-Host "[BUILD] Building container (this may take a few minutes)..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$ProjectId/$ServiceName --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[DEPLOY] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image gcr.io/$ProjectId/$ServiceName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-secrets GITHUB_TOKEN=github-token:latest `
    --set-env-vars FLASK_ENV=production,LOG_LEVEL=INFO,CACHE_DIR=/app/cache `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 10 `
    --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}

# Get service URL
$serviceUrl = gcloud run services describe $ServiceName --region $Region --format "value(status.url)"

Write-Host ""
Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Service URL: $serviceUrl" -ForegroundColor White
Write-Host ""

# Test endpoints
Write-Host "[TEST] Testing endpoints..." -ForegroundColor Yellow
try {
    Write-Host "Testing stats endpoint..." -ForegroundColor Gray
    $statsResponse = Invoke-RestMethod -Uri "$serviceUrl/api/stats" -TimeoutSec 10
    Write-Host "Stats: total_chunks=$($statsResponse.total_chunks), total_articles=$($statsResponse.total_articles)" -ForegroundColor White
    
    Write-Host "Testing ask endpoint..." -ForegroundColor Gray
    $askBody = @{ question = "What is Python?" } | ConvertTo-Json
    $askResponse = Invoke-RestMethod -Uri "$serviceUrl/api/ask" -Method Post -Body $askBody -ContentType "application/json" -TimeoutSec 30
    Write-Host "[OK] API is responding correctly" -ForegroundColor Green
} catch {
    Write-Host "[WARN] API test failed (service may need a moment to warm up)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[COSTS] Cost Estimate (Free Tier):" -ForegroundColor Cyan
Write-Host "- Cloud Run: 2M requests/month FREE" -ForegroundColor White
Write-Host "- Cloud Storage: 5GB FREE" -ForegroundColor White
Write-Host "- Secret Manager: 6 active versions FREE" -ForegroundColor White
Write-Host "- Expected cost: `$0-5/month for low-moderate traffic" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. [OK] Backend deployed: $serviceUrl" -ForegroundColor White
Write-Host "2. Optional - Configure Firebase Hosting:" -ForegroundColor White
Write-Host "   - Run: firebase login" -ForegroundColor Gray
Write-Host "   - Run: firebase init hosting" -ForegroundColor Gray
Write-Host "   - Edit firebase.json to rewrite to Cloud Run" -ForegroundColor Gray
Write-Host "   - Run: firebase deploy --only hosting" -ForegroundColor Gray
Write-Host "3. Optional - Set up CI/CD (see FIREBASE_DEPLOYMENT.md step 7)" -ForegroundColor White
Write-Host "4. Monitor logs: gcloud logging tail `"resource.type=cloud_run_revision`"" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "- Full guide: FIREBASE_DEPLOYMENT.md" -ForegroundColor White
Write-Host "- Security: SECURITY.md" -ForegroundColor White
