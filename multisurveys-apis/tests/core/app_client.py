"""A TestClient for one of the APIs, on the test database.

Each api.py ends with ``app = CORSMiddleware(app, ...)``, so ``<api>.api.app`` is the CORS wrapper and the
FastAPI app (with ``.state``) is inside it. The client goes through the wrapper, as production does.
"""

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PACKAGE_DIR = Path(__file__).resolve().parents[2]


def client_for(api: str, db=None, **kwargs) -> TestClient:
    # probability and aladin import "src.…", which resolves from the package dir, as in production
    if str(PACKAGE_DIR) not in sys.path:
        sys.path.append(str(PACKAGE_DIR))
    # Imported here: each app builds its engine at import, from the env the db fixture sets
    app = importlib.import_module(f"{api}.api").app
    if db is not None:
        fastapi_app(app).state.psql_session = db.session
    # The root_path run_api.py gives the server in production
    return TestClient(app, root_path=f"/{api}", **kwargs)


def fastapi_app(app):
    return getattr(app, "app", app)
