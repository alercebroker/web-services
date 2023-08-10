from flask import Flask
from ralidator_flask.ralidator_flask import RalidatorFlask

TEST_SECRET_KEY = "test_key"

app = Flask(__name__)
app.config["FILTERS_MAP"] = {}
app.config["RALIDATOR_SETTINGS"] = {
    "USER_API_URL": "user_api_url",
    "USER_API_TOKEN": "user_api_token",
    "SECRET_KEY": TEST_SECRET_KEY,
}
ralidator = RalidatorFlask(app)


@app.route("/")
def hello_world():
    return "Hello World"
