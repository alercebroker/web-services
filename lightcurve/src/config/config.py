import os


def app_config():
    return {
        "ralidator": {
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "ignore_paths": ["/docs", "/metrics", "/openapi.json"],
            "ignore_prefixes": ["/static", "/htmx", '/object','/magStat'],
        },
        "tid": ["atlas", "ztf", "all"],
    }
