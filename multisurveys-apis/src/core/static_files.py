"""
Static files served under a versioned path, so browsers fetch new JS and CSS after each deploy.

Templates reference assets as ``{{ ASSETS_URL }}/static/...``, where ``ASSETS_URL`` is
``<API_URL>/v/<version>``. A new release changes the path, so browsers can cache each copy forever
(``immutable``) and still never run old JS against new HTML. The version lives in the path rather than in a
``?v=`` query because ES modules import each other by relative path, which drops the query string but keeps
the path.

The unversioned paths keep working for anything that links them directly.
"""

import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .version import APP_VERSION

VERSIONED_PREFIX = f"/v/{APP_VERSION}"
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"


class VersionedStaticFiles(StaticFiles):
    """StaticFiles whose responses may be cached forever, because their path changes with every release."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = IMMUTABLE_CACHE_CONTROL
        return response


def mount_static(app: FastAPI, path: str, directory, name: str):
    """Serve ``directory`` at both ``path`` and its versioned twin ``/v/<version><path>``.

    Explicit routes, not ``app.mount()``: the APIs set ``root_path`` so their /docs work behind the nginx
    sidecar, which strips that prefix. A StaticFiles mount resolves files against the accumulated root_path
    and 404s on the stripped path; a route matches it (see DEPLOYMENT.md, "The root_path / prefix-strip gotcha").
    """
    _static_route(app, path, StaticFiles(directory=directory), name)
    _static_route(app, f"{VERSIONED_PREFIX}{path}", VersionedStaticFiles(directory=directory), f"{name}-versioned")


def _static_route(app: FastAPI, prefix: str, files: StaticFiles, name: str):
    # async because get_response is: it reads the file without blocking, so it doesn't hold a thread
    async def serve(path: str, request: Request):
        return await files.get_response(path, request.scope)

    app.add_api_route(f"{prefix}/{{path:path}}", serve, methods=["GET", "HEAD"], name=name, include_in_schema=False)


def configure_templates(templates: Jinja2Templates, default_api_url: str):
    """Expose ``API_URL``, ``APP_VERSION`` and ``ASSETS_URL`` (the versioned asset base) to the templates."""
    api_url = os.getenv("API_URL", default_api_url)
    templates.env.globals["API_URL"] = api_url
    templates.env.globals["APP_VERSION"] = APP_VERSION
    templates.env.globals["ASSETS_URL"] = f"{api_url}{VERSIONED_PREFIX}"
