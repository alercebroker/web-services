import os
from flask_cors import CORS
from flask import Flask
import logging
from flask_caching import Cache

# Starting Flask API
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# Init cache
cache.init_app(app)
#Adding CORS for async calls
CORS(app)

#Check if gunicorn for logging
is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
if is_gunicorn:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

#Default route
@app.route("/")
def index():
    return "Welcome to ALERCE PSQL API"


from .external import external_blueprint
app.register_blueprint(external_blueprint)