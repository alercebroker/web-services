from werkzeug.middleware.profiler import ProfilerMiddleware
import sys
sys.path.append('..')
from api import app

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.run(debug = True, host='0.0.0.0')