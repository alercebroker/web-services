FROM python:3.11-slim AS python-base
LABEL org.opencontainers.image.authors="ALeRCE"

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1

FROM python-base AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry;

COPY tns_api/poetry.lock tns_api/pyproject.toml /app/

WORKDIR /app
RUN poetry install --no-root --without=dev --without=test;

FROM python:3.11-slim AS production
RUN pip install poetry;

COPY --from=builder /app /app

COPY tns_api/tns_api /app/tns_api
COPY tns_api/scripts /app/scripts
COPY tns_api/README.md \
  /app/

WORKDIR /app
RUN poetry install --only-root;

CMD ["poetry", "run", "build_parquet"]
