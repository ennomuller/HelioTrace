# ---------------------------------------------------------------------------
# HelioTrace — production Docker image
#
# Build:   docker build -t heliotrace .
# Run:     docker run -p 8501:8501 heliotrace
# Compose: docker-compose up
# ---------------------------------------------------------------------------

FROM python:3.11-slim

# --- Environment hygiene ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# --- System build tools (needed for scipy / numpy wheels) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies first (cache layer) ---
# Only copy the package manifest so this layer re-runs only when deps change.
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

# --- Copy application code ---
COPY app.py ./
COPY pages/ ./pages/
COPY .streamlit/ ./.streamlit/

# --- Health check & port ---
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# --- Launch ---
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]