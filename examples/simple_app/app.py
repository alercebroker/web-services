from flask import Flask
from ralidator_flask.ralidator_flask import RalidatorFlask


app = Flask(__name__)
app.config["FILTERS_MAP"] = {}
ralidator = RalidatorFlask(app)


@app.route("/")
def hello_world():
    return "Hello World"
