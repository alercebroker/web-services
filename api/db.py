from db_plugins.db.sql import DatabaseConnection, BaseQuery

session_options = {
    "autocommit": False,
    "autoflush": False,
    "query_cls": BaseQuery,
}

db = DatabaseConnection()
