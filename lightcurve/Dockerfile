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
COPY ./lightcurve/poetry.lock ./lightcurve/pyproject.toml /app
COPY ./libs/ralidator-core /libs/ralidator-core
COPY ./libs/ralidator-fastapi /libs/ralidator-fastapi
RUN poetry install --no-root --without=test


FROM python:3.11-slim as production
RUN pip install poetry
COPY --from=builder /app /app
COPY --from=builder /libs /libs
WORKDIR /app
COPY ./lightcurve/README.md /app/README.md
COPY ./lightcurve/scripts /app/scripts
COPY ./lightcurve/src /app/src
RUN poetry install --only-root --without=test
CMD ["bash", "scripts/entrypoint.sh"]
