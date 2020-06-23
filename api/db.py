from db_plugins.db import SQLDatabase
from db_plugins.db.sql import SQLQuery

session_options = {
    "autocommit": False,
    "autoflush": False,
    "query_cls": SQLQuery,
}

db = SQLDatabase()
