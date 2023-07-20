#!/usr/bin/env sh

echo "Starting ZTF API"
run="poetry run memray run -o /app/tests/profiling/memray_graph.bin --follow-fork -m gunicorn -c gunicorn_config.py --bind 0.0.0.0:$PORT --worker-class gthread -w $APP_WORKERS --threads $THREADS --log-level=$LOG_LEVEL src.api.app:create_app('config.yml')"
$run
