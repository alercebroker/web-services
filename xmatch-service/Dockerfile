FROM python:3.11-slim as base
LABEL org.opencontainers.image.authors="ALeRCE"
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1

FROM base as builder
RUN pip install poetry
WORKDIR /app
COPY ./xmatch-service/poetry.lock ./xmatch-service/pyproject.toml /app
RUN poetry install --no-root --without=test

FROM python:3.11-slim as production
RUN pip install poetry
COPY --from=builder /app /app
WORKDIR /app
COPY ./xmatch-service/README.md /app/README.md
COPY ./xmatch-service/src /app/src
RUN poetry install --only-root
CMD ["poetry", "run", "uvicorn", "http_server.api:app", "--host", "0.0.0.0", "--port", "8000"]
