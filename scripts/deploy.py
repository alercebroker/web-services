#!/usr/bin/env python3
import sys
sys.path.append("..")
from api import app
if __name__ == "__main__":
    app.run(debug=args.debug, port=args.port)
