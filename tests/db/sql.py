from db_plugins.db.sql import *
from db_plugins.db.sql.models import *
import unittest
import pytest
import json
import requests

import os
import sys

FILE_PATH = os.path.dirname(os.path.abspath(os.curdir))
sys.path.append(FILE_PATH)

from api import app, db
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = {
        'SQL': 'sqlite:///:memory:'
    }
    with app.test_client() as c:
        with app.app_context():
            db.init_db()
            return c


def test_class(client):
    print("TEST", app.config["DATABASE"])
    print(client.get("/class").json)
    pass