#!/usr/bin/env sh

poetry run uvicorn --port $PORT api.api:app