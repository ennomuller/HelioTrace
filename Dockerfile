# ---------------------------------------------------------------------------
# HelioTrace — production Docker image
#
# Build:   docker build -t heliotrace .
# Run:     docker run -p 8501:8501 heliotrace
# Compose: docker compose up
# ---------------------------------------------------------------------------

FROM python:3.13-slim

# --- Install uv from the official image ---
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- Environment hygiene ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# --- Install Python dependencies first (cache layer) ---
# Copy manifest + lock file so this layer re-runs only when deps change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-dev --no-install-project

# --- Copy application source and install the local package ---
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-dev

# --- Copy application code ---
COPY app.py ./
COPY pages/ ./pages/
COPY .streamlit/ ./.streamlit/

# --- Health check & port ---
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# --- Launch (use the venv created by uv) ---
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
