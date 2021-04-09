from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
from prometheus_flask_exporter import PrometheusMetrics
import os

is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
if is_gunicorn:
    prometheus_metrics = GunicornInternalPrometheusMetrics.for_app_factory()
else:
    prometheus_metrics = PrometheusMetrics.for_app_factory()
