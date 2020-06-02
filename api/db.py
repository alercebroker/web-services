from db_plugins.db.sql import get_scoped_session, start_db
from flask import current_app 
session = get_scoped_session(current_app.config["DATABASE"]["SQL"])

def init_db():
    start_db(current_app.config["DATABASE"]["SQL"])

def close_session(e=None):
    if session is not None:
        session.remove()

def init_app(app):
    app.teardown_appcontext(close_session)
