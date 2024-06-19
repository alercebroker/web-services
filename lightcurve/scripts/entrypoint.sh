#!/usr/bin/env sh

poetry run uvicorn --host 0.0.0.0 --port $PORT $SERVICE.api:app
