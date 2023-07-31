#!/usr/bin/env sh

poetry run uvicorn --port $PORT api.main:create_app --factory