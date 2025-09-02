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

COPY multisurvey-stamps/pyproject.toml multisurvey-stamps/poetry.lock /app/

WORKDIR /app
RUN poetry install --no-root --without=test;


FROM python:3.11-slim AS production
RUN pip install poetry;

COPY --from=builder /app /app

COPY multisurvey-stamps/src /app/src
COPY multisurvey-stamps/scripts /app/scripts
COPY multisurvey-stamps/README.md /app/

WORKDIR /app
RUN poetry install --only-root;

CMD ["poetry", "run", "service"]
