#!/usr/bin/env sh

poetry run uvicorn --host 0.0.0.0 --port $PORT api.main:create_app --factory