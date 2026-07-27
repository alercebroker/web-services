#!/bin/bash
echo "Starting ZTF API"
run="poetry run gunicorn -c gunicorn_config.py --bind 0.0.0.0:$PORT --worker-class gthread -w $APP_WORKERS --threads $THREADS --log-level=$LOG_LEVEL src.api.app:create_app('config.yml')"
# exec so gunicorn becomes pid 1 and receives SIGTERM directly. Without it bash
# stays pid 1, never forwards the signal, and every stop is a SIGKILL at the end
# of the grace period (exit 137) that drops in-flight requests instead of draining.
exec $run
