# ═══════════════════════════════════════════════════════════════════════════════
# Dockerfile — Zomato AI Restaurant Recommendation Service
# Multi-stage build optimised for Google Cloud Run
#
# Stage 1 (builder): pip install all deps into a prefix dir so Stage 2
#                    copies only the byte-compiled site-packages — no pip,
#                    no build tools, no cache bleed.
# Stage 2 (runtime): Distroless-style slim Python image; non-root user;
#                    Streamlit on port 8080 (Cloud Run convention).
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Stage 1 · Builder ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Keep pip quiet; never write .pyc in the build stage
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# Copy only the dependency manifest first (maximises layer caching)
COPY requirements.txt .

# Install into an isolated prefix so we can COPY just site-packages
RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements.txt

# ─── Stage 2 · Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# ── Labels (OCI image spec) ───────────────────────────────────────────────────
LABEL org.opencontainers.image.title="Zomato AI Restaurant Recommendation"
LABEL org.opencontainers.image.description="Streamlit app – HF Zomato dataset with AI-powered filters"
LABEL org.opencontainers.image.source="https://github.com/YOUR_ORG/zomato-ai"

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Tell Python where the builder's site-packages live
    PYTHONPATH=/app \
    # Streamlit reads this in headless mode
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    # HuggingFace offline cache dir inside container
    HF_HOME=/tmp/hf_cache \
    TRANSFORMERS_CACHE=/tmp/hf_cache

# ── Copy installed packages from builder ──────────────────────────────────────
COPY --from=builder /install/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages

# ── Create non-root user for Cloud Run best practice ─────────────────────────
RUN addgroup --system appgroup \
 && adduser  --system --ingroup appgroup --no-create-home appuser

WORKDIR /app

# ── Copy project source ───────────────────────────────────────────────────────
COPY --chown=appuser:appgroup . /app

# ── Switch to non-root ────────────────────────────────────────────────────────
USER appuser

# ── Expose Cloud Run's expected port ─────────────────────────────────────────
EXPOSE 8080

# ── Health-check (Cloud Run uses HTTP; Streamlit's /_stcore/health works) ─────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/_stcore/health')"

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py", \
            "--server.port=8080", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--server.enableCORS=false", \
            "--server.enableXsrfProtection=false"]
