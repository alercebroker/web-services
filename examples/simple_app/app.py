from flask import Flask
from ralidator_flask.ralidator_flask import RalidatorFlask

TEST_SECRET_KEY = "test_key"

app = Flask(__name__)
app.config["FILTERS_MAP"] = {}
app.config["RALIDATOR_SETTINGS"] = {
    "user_api_url": "user_api_url",
    "user_api_token": "user_api_token",
    "secret_key": TEST_SECRET_KEY,
}
ralidator = RalidatorFlask(app)


@app.route("/")
def hello_world():
    return "Hello World"
