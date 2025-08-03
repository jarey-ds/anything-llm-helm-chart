# Build stage
FROM python:3.11-slim AS builder

# Install uv for build stage only
COPY --from=ghcr.io/astral-sh/uv:0.7.15 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock alembic.ini ./
COPY src ./src

# Install dependencies using uv workspace with mounted secrets
RUN --mount=type=secret,id=pip-netrc,target=/root/.netrc \
    --mount=type=secret,id=pip-config,target=/root/.config/pip/pip.conf \
    uv sync --frozen --no-dev --package sso_anythingllm_rest

# Final stage
FROM python:3.11-slim

LABEL org.opencontainers.image.title="Keycloak SSO AnythingLLM integration."
LABEL org.opencontainers.image.authors="jose@dataspartan.com"
LABEL org.opencontainers.image.description="API to manage access via simple SSO support to AnythingLLM."

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV API_PORT=8000
ARG APP_DIR=/app

# Copy installed packages from builder
COPY --from=builder ${APP_DIR}/.venv ${APP_DIR}/.venv

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools

# Set working directory
WORKDIR ${APP_DIR}

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy application code
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser pyproject.toml uv.lock alembic.ini ./

# openshift compability
RUN chown -R appuser:appuser ${APP_DIR} \
    && chgrp -R 0 ${APP_DIR} && chmod -R g=u ${APP_DIR}

# Remove packages
RUN pip uninstall pip -y 

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$API_PORT/monitoring/health || exit 1

CMD /app/.venv/bin/uvicorn sso_anythingllm_rest.main:app --host 0.0.0.0 --port $API_PORT
