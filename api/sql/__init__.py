from .settings import DB_CONFIG
from db_plugins.db.sql import get_session
session = get_session(DB_CONFIG)