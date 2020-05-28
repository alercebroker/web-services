from .sql.sql import sql_api
import os
from flask_cors import CORS
from flask import Flask
import logging
from flask_caching import Cache
from settings import PROFILE_CONFIG
import flask_profiler
from flask_restful_swagger_3 import get_swagger_blueprint
from flask_swagger_ui import get_swaggerui_blueprint


# Starting Flask API
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

app.config["flask_profiler"] = PROFILE_CONFIG


# Init cache
cache.init_app(app)
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
