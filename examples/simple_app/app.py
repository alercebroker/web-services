from flask import Flask
from ralidator_flask import RalidatorFlask

app = Flask(__name__)
ralidator = RalidatorFlask(app)


@app.route("/")
def hello_world():
    return "Hello World"
