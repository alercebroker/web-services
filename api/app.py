from flask import Flask
from api.sql import sql_api

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    sql_api.init_app(app)

    with app.app_context():
        from .db import db, session_options
        db.start(app.config["DATABASE"]["SQL"], session_options=session_options)
        db.create_scoped_session()
        def cleanup(e):
            db.session.remove()
            return e
        app.teardown_appcontext(cleanup)
    return app