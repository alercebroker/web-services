import pathlib
import re

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

from core.static_files import IMMUTABLE_CACHE_CONTROL, VERSIONED_PREFIX, configure_templates, mount_static
from core.version import APP_VERSION

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"


def test_versioned_prefix_carries_the_package_version():
    assert VERSIONED_PREFIX == f"/v/{APP_VERSION}"


def test_mount_static_serves_both_paths_and_only_the_versioned_one_is_immutable(tmp_path):
    (tmp_path / "app.js").write_text("console.log('hi')")
    app = FastAPI()
    mount_static(app, "/static", tmp_path, "static")
    client = TestClient(app)

    plain = client.get("/static/app.js")
    versioned = client.get(f"{VERSIONED_PREFIX}/static/app.js")

    assert plain.status_code == versioned.status_code == 200
    assert plain.text == versioned.text
    assert "cache-control" not in plain.headers
    assert versioned.headers["cache-control"] == IMMUTABLE_CACHE_CONTROL


def test_configure_templates_sets_the_asset_base(monkeypatch):
    monkeypatch.setenv("API_URL", "https://api.example.org/object_api")
    templates = Jinja2Templates(directory=".")
    configure_templates(templates, "http://localhost:8000")

    assert templates.env.globals["API_URL"] == "https://api.example.org/object_api"
    assert templates.env.globals["ASSETS_URL"] == f"https://api.example.org/object_api{VERSIONED_PREFIX}"


def test_lightcurve_serves_versioned_static_files():
    # Lightcurve sets root_path, so its static files are explicit routes rather than mounts.
    from lightcurve_api.api import app

    client = TestClient(app)
    response = client.get(f"{VERSIONED_PREFIX}/static/lightcurve-app.js")

    assert response.status_code == 200
    assert response.headers["cache-control"] == IMMUTABLE_CACHE_CONTROL


def test_templates_reference_local_assets_through_the_versioned_base():
    # A static file linked through API_URL would be cached by browsers across deploys.
    unversioned = re.compile(r"\{\{\s*API_URL\s*\}\}/(static/|chart/|htmx-static/|libraries/|htmx/[^\"'\s]*\.js)")
    offenders = [
        f"{template.relative_to(SRC)}: {match.group(0)}"
        for template in SRC.rglob("*.jinja")
        for match in unversioned.finditer(template.read_text())
    ]
    assert offenders == []
