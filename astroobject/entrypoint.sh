#!/usr/bin/env sh

poetry run uvicorn --host 0.0.0.0 --port $PORT --root-path $PREFIX api.main:create_app --factory