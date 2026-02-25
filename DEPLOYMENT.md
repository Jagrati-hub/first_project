# 🚀 Zomato AI — Google Cloud Run Deployment Guide

## Architecture Overview

```
GitHub Push (main)
      │
      ▼
Google Cloud Build (cloudbuild.yaml)
      │   ┌─────────────────────────────────────────┐
      ├─► │  Stage 1: Build multi-stage Docker image│
      │   │  Stage 2: Push to Artifact Registry     │
      │   │  Stage 3: Deploy to Cloud Run           │
      │   │  Stage 4: Smoke-test health endpoint    │
      │   └─────────────────────────────────────────┘
      │
      ▼
Cloud Run Service (us-central1)
      │
      ▼
https://zomato-ai-recommender-<hash>-uc.a.run.app
```

---

## Pre-requisites

| Tool | Install |
|---|---|
| Google Cloud SDK | https://cloud.google.com/sdk/docs/install |
| Docker Desktop | https://www.docker.com/products/docker-desktop |
| Docker BuildKit | Enabled by default in Docker 23+ |
| A GCP Project | https://console.cloud.google.com/projectcreate |

---

## Step 1 — One-Time GCP Setup

```bash
# Authenticate
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    containeranalysis.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create zomato-ai \
    --repository-format=docker \
    --location=us-central1 \
    --description="Zomato AI Streamlit images"
```

---

## Step 2 — Local Build & Test (Recommended First)

```bash
# From the project root
docker build -t zomato-ai:local .

# Run locally (mirrors Cloud Run env)
docker run -p 8080:8080 \
    -e STREAMLIT_SERVER_PORT=8080 \
    -e STREAMLIT_SERVER_HEADLESS=true \
    zomato-ai:local

# Open http://localhost:8080
```

---

## Step 3A — Manual Deploy (One-Shot)

### Linux / macOS
```bash
chmod +x deploy/cloud_run_deploy.sh
GCP_PROJECT_ID=your-project-id GCP_REGION=us-central1 \
    ./deploy/cloud_run_deploy.sh
```

### Windows PowerShell
```powershell
.\deploy\cloud_run_deploy.ps1 -ProjectId "your-project-id" -Region "us-central1"
```

---

## Step 3B — CI/CD via Cloud Build (Recommended)

### Connect your GitHub repo
```bash
# Install Cloud Build GitHub App first:
# https://github.com/apps/google-cloud-build

# Create the trigger
gcloud builds triggers create github \
    --repo-name=zomato-ai \
    --repo-owner=YOUR_GITHUB_ORG \
    --branch-pattern='^main$' \
    --build-config=cloudbuild.yaml \
    --substitutions=_REGION=us-central1,_SERVICE=zomato-ai-recommender
```

Every `git push` to `main` will now:
1. Build the Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Run a live smoke-test

---

## Step 4 — Verify Deployment

```bash
# Get the service URL
gcloud run services describe zomato-ai-recommender \
    --region=us-central1 \
    --format="value(status.url)"

# Health check
curl -sf "$(gcloud run services describe zomato-ai-recommender \
    --region=us-central1 --format='value(status.url)')/_stcore/health"
# Expected: {"status": "ok"}

# View live logs
gcloud run services logs read zomato-ai-recommender \
    --region=us-central1 --limit=50
```

---

## Cloud Run Service Settings

| Parameter | Value | Rationale |
|---|---|---|
| Port | `8080` | Cloud Run default |
| Memory | `2 GiB` | HF dataset loading needs ~800 MB; headroom for spikes |
| CPU | `1 vCPU` | Streamlit is single-threaded; 1 CPU is sufficient |
| Min instances | `0` | Cost-efficient; scales to zero when idle |
| Max instances | `10` | Cap to control costs |
| Concurrency | `80` | Each Streamlit session uses light memory |
| Timeout | `300s` | 5-min request timeout for slow HF dataset loads |
| Auth | `--allow-unauthenticated` | Public app; remove for private deployment |

---

## Environment Variables

| Variable | Value | Purpose |
|---|---|---|
| `STREAMLIT_SERVER_PORT` | `8080` | Matches `EXPOSE 8080` in Dockerfile |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Disables browser auto-open |
| `HF_HOME` | `/tmp/hf_cache` | HuggingFace cache (ephemeral, writable) |

---

## Cost Estimate (us-central1, Pay-as-you-go)

| Scenario | Est. Monthly Cost |
|---|---|
| 0 requests (idle, min=0) | **$0.00** |
| 1,000 req/day, avg 5s each | **~$1–3** |
| 10,000 req/day, avg 5s each | **~$6–12** |

> Cloud Run has a generous **2M free requests/month** in the free tier.

---

## Rollback

```bash
# List revisions
gcloud run revisions list \
    --service=zomato-ai-recommender \
    --region=us-central1

# Roll back to a previous revision
gcloud run services update-traffic zomato-ai-recommender \
    --region=us-central1 \
    --to-revisions=REVISION_NAME=100
```

---

## Project File Structure (Final)

```
first_project/
├── app.py                          ← Main Streamlit application
├── requirements.txt                ← Python dependencies
├── Dockerfile                      ← Multi-stage production image
├── .dockerignore                   ← Excludes .venv, __pycache__, etc.
├── cloudbuild.yaml                 ← CI/CD pipeline (Cloud Build)
├── .streamlit/
│   └── config.toml                 ← Production Streamlit settings
├── data/
│   └── restaurants.py              ← HF dataset loader + fallback
├── styles/
│   └── styles.py                   ← Glassmorphism CSS
├── components/
│   └── components.py               ← HTML component builders
└── deploy/
    ├── cloud_run_deploy.sh         ← One-shot deploy (bash)
    └── cloud_run_deploy.ps1        ← One-shot deploy (PowerShell)
```
