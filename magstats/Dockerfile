FROM python:3.11 as python-base
LABEL org.opencontainers.image.authors="ALeRCE"
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1


FROM python-base as builder
RUN pip install poetry
WORKDIR /app
COPY ./magstats/poetry.lock ./magstats/pyproject.toml /app
RUN poetry install --no-root --without=test


FROM python:3.11-slim as production
RUN pip install poetry
COPY --from=builder /app /app
WORKDIR /app
COPY ./magstats/README.md /app/README.md
COPY ./magstats/entrypoint.sh /app/
COPY ./magstats/core /app/core
COPY ./magstats/api /app/api
COPY ./magstats/database /app/database
RUN poetry install --only-root
CMD ["bash", "scripts/entrypoint.sh"]