#!/usr/bin/env sh

poetry run uvicorn --port $PORT lightcurve_api.api:app
