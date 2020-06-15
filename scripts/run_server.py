import sys

sys.path.append("..")
from api.app import create_app
import argparse

parser = argparse.ArgumentParser(description="ALERCE Flask API.")
parser.add_argument("--debug", action="store_true", help="Debug Logging level")
parser.add_argument("--port", type=int, help="Local server port")
args = parser.parse_args()

if __name__ == "__main__":
    app = create_app("settings")
    app.run(debug=args.debug, port=args.port)
