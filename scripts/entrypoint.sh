#!/bin/bash
echo "Starting ZTF API"
run="gunicorn -c gunicorn_config.py --bind 0.0.0.0:5000 --worker-class gevent -w $APP_WORKERS --log-level=$LOG_LEVEL api.app:create_app('config.yml')"
$run
