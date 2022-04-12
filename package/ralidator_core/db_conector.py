from db_plugins.db.sql import SQLQuery, SQLConnection

session_options = {
    "autocommit": False,
    "autoflush": False,
    "query_cls": SQLQuery,
}

db = SQLConnection()

class RolesQueries(object):
    
    def get_all_filters(self):
        pass