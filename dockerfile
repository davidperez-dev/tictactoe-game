# ---------------------------------------------------------------------------
# Stage 1 -- Base
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl default-libmysqlclient-dev gcc pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 -- Development  (used by .devcontainer)
# ---------------------------------------------------------------------------
FROM base AS development

RUN pip install --no-cache-dir \
        django-debug-toolbar \
        pytest-django \
        coverage \
        black \
        isort \
        pylint-django

# Source code is bind-mounted at runtime by the devcontainer
EXPOSE 8000

# ---------------------------------------------------------------------------
# Stage 3 -- Production
# ---------------------------------------------------------------------------
FROM base AS production

# Non-root user for security
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --no-create-home appuser

COPY . .

RUN chmod +x entrypoint.sh \
    && mkdir -p django_auth/staticfiles \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
