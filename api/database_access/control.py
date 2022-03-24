from db_plugins.db.sql import models as psql_models
from db_plugins.db.mongo import models as mongo_models
from .psql_db import db as psql_db, session_options
from .mongo_db import db as mongo_db


class DBControl(object):

    # Initialization and cleanup methods
    def __init__(
        self, app_config: dict, psql_config: dict, mongo_config: dict
    ) -> None:
        self.app_config = app_config
        self.psql_config = psql_config
        self.mongo_config = mongo_config

    def connect_databases(self):
        if self.app_config["CONNECT_PSQL"]:
            self.connect_psql()
        if self.app_config["CONNECT_MONGO"]:
            self.connect_mongo()

    def connect_psql(self):
        psql_db.connect(
            config=self.psql_config,
            session_options=session_options,
            use_scoped=True,
        )

    def connect_mongo(self):
        mongo_db.connect(config=self.mongo_config)

    def cleanup_databases(self, e):
        if self.app_config["CONNECT_PSQL"]:
            self.cleanup_psql()
        if self.app_config["CONNECT_MONGO"]:
            self.cleanup_mongo()
        return e

    def cleanup_psql(self):
        psql_db.session.remove()

    def cleanup_mongo(self):
        pass
