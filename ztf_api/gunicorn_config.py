from prometheus_flask_exporter.multiprocess import (
    GunicornInternalPrometheusMetrics,
)
import os


def child_exit(server, worker):
    environment = os.environ.get("ENVIRONMENT", "develop")
    if environment == "production":  # pragma: no cover
        GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(
            worker.pid
        )
