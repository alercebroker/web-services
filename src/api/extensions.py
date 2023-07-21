from ralidator_flask.ralidator_flask import RalidatorFlask
import os


ralidator = RalidatorFlask()
is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
environment = os.environ.get("ENVIRONMENT", "develop")

if environment == "production":  # pragma: no cover
    from prometheus_flask_exporter.multiprocess import (
        GunicornInternalPrometheusMetrics,
    )
    from prometheus_flask_exporter import PrometheusMetrics

    if is_gunicorn:
        prometheus_metrics = (
            GunicornInternalPrometheusMetrics.for_app_factory()
        )
    else:
        prometheus_metrics = PrometheusMetrics.for_app_factory()
else:

    class Mock:
        def init_app(self, app):
            return None

    prometheus_metrics = Mock()
