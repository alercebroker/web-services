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
COPY ./poetry.lock ./pyproject.toml ./
COPY ./README.md /app/README.md
RUN poetry install --no-root --without=dev


FROM python:3.11-slim as production
RUN pip install poetry
COPY --from=builder /app /app
WORKDIR /app
COPY ./config.yml /app/
COPY ./core /app/core
COPY ./api /app/api
COPY ./entrypoint.sh /app/
RUN poetry install --only-root
CMD ["bash", "entrypoint.sh"]
