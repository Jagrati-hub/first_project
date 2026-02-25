# deploy/cloud_run_deploy.ps1
# ============================================================
# PowerShell equivalent of cloud_run_deploy.sh (Windows users)
# ============================================================

param(
    [string]$ProjectId  = $env:GCP_PROJECT_ID ?? "your-gcp-project-id",
    [string]$Region     = $env:GCP_REGION     ?? "us-central1",
    [string]$ServiceName = "zomato-ai-recommender",
    [string]$RepoName    = "zomato-ai"
)

$ErrorActionPreference = "Stop"

# Derived values
$ImageTag    = (git rev-parse --short HEAD 2>$null) ?? "latest"
$ArHost      = "${Region}-docker.pkg.dev"
$ImageUri    = "${ArHost}/${ProjectId}/${RepoName}/${ServiceName}:${ImageTag}"
$CacheUri    = "${ArHost}/${ProjectId}/${RepoName}/${ServiceName}:cache"

Write-Host "🔧  Checking Artifact Registry repo '${RepoName}'…" -ForegroundColor Cyan
$repoExists = gcloud artifacts repositories describe $RepoName `
    --project=$ProjectId --location=$Region 2>$null
if (-not $repoExists) {
    gcloud artifacts repositories create $RepoName `
        --project=$ProjectId --location=$Region `
        --repository-format=docker `
        --description="Zomato AI Docker images"
}

Write-Host "🐳  Building Docker image → ${ImageUri}" -ForegroundColor Cyan
docker build `
    --platform linux/amd64 `
    --tag $ImageUri `
    --cache-from $CacheUri `
    --build-arg BUILDKIT_INLINE_CACHE=1 `
    .

Write-Host "📤  Pushing image…" -ForegroundColor Cyan
docker push $ImageUri
docker tag $ImageUri $CacheUri
docker push $CacheUri

Write-Host "☁️   Deploying to Cloud Run (${Region})…" -ForegroundColor Cyan
gcloud run deploy $ServiceName `
    --project=$ProjectId `
    --region=$Region `
    --image=$ImageUri `
    --platform=managed `
    --port=8080 `
    --allow-unauthenticated `
    --memory=2Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=10 `
    --concurrency=80 `
    --timeout=300 `
    "--set-env-vars=STREAMLIT_SERVER_PORT=8080,STREAMLIT_SERVER_HEADLESS=true,HF_HOME=/tmp/hf_cache" `
    "--labels=app=zomato-ai,env=production"

$ServiceUrl = gcloud run services describe $ServiceName `
    --project=$ProjectId --region=$Region `
    --format="value(status.url)"

Write-Host ""
Write-Host "✅  Deployment complete!" -ForegroundColor Green
Write-Host "🌐  Live URL: $ServiceUrl"   -ForegroundColor Green
Write-Host ""
Write-Host "Smoke-test:" -ForegroundColor Yellow
Write-Host "  Invoke-WebRequest '${ServiceUrl}/_stcore/health'"
