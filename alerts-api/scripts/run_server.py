from api.app import create_app
import argparse

# Load environment variables from .env file
# from dotenv import load_dotenv
# load_dotenv()

parser = argparse.ArgumentParser(description="ALERCE Flask API.")
parser.add_argument("--debug", action="store_true", help="Debug Logging level")
parser.add_argument("--port", type=int, help="Local server port")
args = parser.parse_args()

if __name__ == "__main__":
    app = create_app("config.yml")
    app.run(debug=args.debug, port=args.port)
