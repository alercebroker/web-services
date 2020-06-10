from flask import Flask
from api.sql import sql_api
from db_plugins.db.sql.models import Base
def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    sql_api.init_app(app)

    from api.db import db
    with app.app_context():
        db.init_app(app.config["DATABASE"], Base)
        db.create_scoped_session()
        app.teardown_appcontext(db.cleanup)
    return app