import pytest
import sys

sys.path.append("..")
from api.app import create_app
from api.db import db
from db_plugins.db.sql.models import Base


@pytest.fixture
def client():

    app = create_app('settings')

    with app.test_client() as client:
        with app.app_context():
            db.init_app(app.config["DATABASE"], Base)
            db.create_scoped_session()
            db.create_db()
            app.teardown_appcontext(db.cleanup)
        yield client
    db.drop_db()

def test_empty_db(client):
    response = client.get("/objects/")
    assert response.status_code == 404
