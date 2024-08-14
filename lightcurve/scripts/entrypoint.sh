#!/usr/bin/env sh

poetry run uvicorn --port $PORT $SERVICE.api:app
