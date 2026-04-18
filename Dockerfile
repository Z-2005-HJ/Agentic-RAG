FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

WORKDIR /app

# Copy configuration files
COPY pyproject.toml uv.lock ./

# UV_COMPILE_BYTECODE for generating .pyc files -> faster application startup.
# UV_LINK_MODE=copy to silence warnings about not being able to use hard links
# since the cache and sync target are on separate file systems.
# Increase HTTP timeout/retries for large dependency downloads on unstable networks.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_HTTP_TIMEOUT=300 UV_HTTP_RETRIES=5

# Default PyPI index; override on restricted networks, e.g.:
# docker compose build --build-arg UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple api
ARG UV_INDEX_URL=https://pypi.org/simple
ENV UV_INDEX_URL=${UV_INDEX_URL}

# uv.lock pins wheels to files.pythonhosted.org; on some campus networks that host fails TLS.
# Set UV_REWRITE_HOSTED_PACKAGES=true with a domestic mirror build (see UV_INDEX_URL above).
ARG UV_REWRITE_HOSTED_PACKAGES=false
RUN if [ "$UV_REWRITE_HOSTED_PACKAGES" = "true" ]; then \
      sed -i 's|https://files.pythonhosted.org/packages|https://pypi.tuna.tsinghua.edu.cn/packages|g' uv.lock; \
    fi

# Install dependencies without BuildKit-only mount flags
RUN uv sync --frozen --no-dev

# Copy source code
COPY src /app/src

FROM python:3.12.8-slim AS final

EXPOSE 8000

# PYTHONUNBUFFERED=1 to disable output buffering
ENV PYTHONUNBUFFERED=1
ARG VERSION=0.1.0
ENV APP_VERSION=$VERSION

WORKDIR /app

# Copy the virtual environment from the base stage
COPY --from=base /app /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 