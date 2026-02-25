#!/usr/bin/env bash
# =============================================================================
# deploy/cloud_run_deploy.sh
# One-shot deployment script for Zomato AI → Google Cloud Run
#
# Prerequisites (run once):
#   gcloud auth login
#   gcloud auth configure-docker
#   gcloud services enable run.googleapis.com artifactregistry.googleapis.com
#
# Usage:
#   chmod +x deploy/cloud_run_deploy.sh
#   ./deploy/cloud_run_deploy.sh
# =============================================================================

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
# Edit these four variables before running.
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"     # GCP project
REGION="${GCP_REGION:-us-central1}"                      # Cloud Run region
SERVICE_NAME="zomato-ai-recommender"                     # Cloud Run service name
REPO_NAME="zomato-ai"                                    # Artifact Registry repo

# Derived
IMAGE_TAG="$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')"
AR_HOST="${REGION}-docker.pkg.dev"
IMAGE_URI="${AR_HOST}/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

# ─── 1. Ensure Artifact Registry repo exists ──────────────────────────────────
echo "🔧  Ensuring Artifact Registry repository '${REPO_NAME}' exists…"
gcloud artifacts repositories describe "${REPO_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" > /dev/null 2>&1 \
|| gcloud artifacts repositories create "${REPO_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --repository-format=docker \
    --description="Zomato AI Docker images"

# ─── 2. Build & push image ────────────────────────────────────────────────────
echo "🐳  Building Docker image → ${IMAGE_URI}"
docker build \
    --platform linux/amd64 \
    --tag "${IMAGE_URI}" \
    --cache-from "${AR_HOST}/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:cache" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

echo "📤  Pushing image to Artifact Registry…"
docker push "${IMAGE_URI}"

# Also tag as 'latest' for cache warm-up on next build
docker tag "${IMAGE_URI}" \
    "${AR_HOST}/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:cache"
docker push "${AR_HOST}/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:cache"

# ─── 3. Deploy to Cloud Run ───────────────────────────────────────────────────
echo "☁️   Deploying to Cloud Run (${REGION})…"
gcloud run deploy "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --image="${IMAGE_URI}" \
    --platform=managed \
    --port=8080 \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=80 \
    --timeout=300 \
    --set-env-vars="STREAMLIT_SERVER_PORT=8080,STREAMLIT_SERVER_HEADLESS=true,HF_HOME=/tmp/hf_cache" \
    --labels="app=zomato-ai,env=production"

# ─── 4. Retrieve deployed URL ─────────────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format="value(status.url)")

echo ""
echo "✅  Deployment complete!"
echo "🌐  Live URL: ${SERVICE_URL}"
echo ""
echo "Run the smoke-test below to verify the service is healthy:"
echo "  curl -sf '${SERVICE_URL}/_stcore/health' && echo 'HEALTHY' || echo 'NOT READY'"
