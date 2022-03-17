from psycogreen.gevent import patch_psycopg
from gevent import monkey

patch_psycopg()
monkey.patch_all()

from api.app import create_app
