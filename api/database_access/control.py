
from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from .psql_db import db as psql_db, session_options
from .mongo_db import db as mongo_db

class DBControl(object):

    # Initialization and cleanup methods
    def __init__(self, psql_config: dict, mongo_config: dict) -> None:
        self.psql_config = psql_config
        self.mongo_config = mongo_config

    def connect_databases(self):
        self.connect_psql()
        self.connect_mongo()

    def connect_psql(self):
        psql_db.connect(
            config=self.psql_config,
            session_options=session_options,
            use_scoped=True
        )

    def connect_mongo(self):
        mongo_db.connect(
            config=self.mongo_config
        )

    def cleanup_databases(self, e):
        self.cleanup_psql()
        self.cleanup_mongo()
        return e

    def cleanup_psql(self):
        psql_db.session.remove()

    def cleanup_mongo(self):
        pass