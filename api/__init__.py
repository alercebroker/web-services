import os
from flask_cors import CORS
from flask import Flask
import logging
from settings import PROFILE_CONFIG, DB_CONFIG
import flask_profiler
from flask_restful_swagger_3 import get_swagger_blueprint
from flask_swagger_ui import get_swaggerui_blueprint

def get_credentials_from_config(config):
    db_credentials = None
    if "PSQL" in config:
        psql_config = config["PSQL"]
        db_credentials = 'postgresql://{}:{}@{}:{}/{}'.format(
            psql_config["USER"], psql_config["PASSWORD"], psql_config["HOST"], psql_config["PORT"], psql_config["DB_NAME"])
    elif "SQLITE" in config:
        db_credentials = 'sqlite:///:memory:'
    return db_credentials


# Starting Flask API
app = Flask(__name__, instance_relative_config=True)
app.config['JSON_SORT_KEYS'] = False
app.config["flask_profiler"] = PROFILE_CONFIG
app.config["DATABASE"] = {"SQL": get_credentials_from_config(DB_CONFIG)}

from .db import session, init_db
@app.teardown_appcontext
def cleanup(resp_or_exc):
    session.remove()    

# Adding CORS for async calls
CORS(app)
# Get SQLAlchemy Session

# Check if gunicorn for logging
is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
if is_gunicorn:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# #Default route
@app.route("/")
def index():
    return "Welcome to ALERCE PSQL API test"


docs = []
from .sql.sql import sql_api

docs.append(sql_api.get_swagger_doc())
app.register_blueprint(sql_api.blueprint)
app.register_blueprint(get_swagger_blueprint(docs))
app.register_blueprint(get_swaggerui_blueprint(
    '/docs',
    'http://localhost:8085/api/swagger.json',
    config={
        "app_name": "ZTF API"
    }
), url_prefix='/docs')


flask_profiler.init_app(app)
