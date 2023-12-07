FROM python:3.10 as python-base
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
ARG WITH_ENV
RUN pip install poetry
WORKDIR /app
COPY ./alerts-api/poetry.lock ./alerts-api/pyproject.toml ./
RUN poetry install --no-root --without=dev --without=test


FROM python:3.10-slim as production
RUN pip install poetry
COPY --from=builder /app /app
WORKDIR /app
ENV APP_WORKERS="1"
ENV ENVIRONMENT="production"
ENV SERVER_SOFTWARE="gunicorn"
ENV PROMETHEUS_MULTIPROC_DIR="/tmp"
COPY ./alerts-api/README.md /app/README.md
COPY ./alerts-api/description.md /app/description.md
COPY ./alerts-api/gunicorn_config.py /app/gunicorn_config.py
COPY ./alerts-api/config.yml /app/config.yml
COPY ./alerts-api/scripts /app/scripts
COPY ./alerts-api/src /app/src
RUN poetry install --only-root
CMD ["/bin/bash","scripts/entrypoint.sh"]
