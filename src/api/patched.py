from psycogreen.gevent import patch_psycopg
from gevent import monkey
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

patch_psycopg()
monkey.patch_all()

from .app import create_app
