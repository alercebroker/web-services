#!/bin/bash
echo "Starting ZTF API"
run="gunicorn --bind 0.0.0.0:8082 --workers $APP_WORKERS --threads $APP_THREADS api.app:create_app('settings')"
$run