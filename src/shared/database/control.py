import signal
import time
from db_plugins.db.sql.connection import SQLConnection, SQLQuery
from db_plugins.db.mongo.connection import MongoConnection
from flask import current_app


class DBControl(object):
    # Initialization and cleanup methods
    def __init__(
        self,
        app_config: dict,
        psql_config: dict,
        mongo_config: dict,
        psql_db: SQLConnection,
        mongo_db: MongoConnection,
    ) -> None:
        self.app_config = app_config
        self.psql_config = psql_config
        SQLALCHEMY_DATABASE_URL = f"postgresql://{psql_config['USER']}:{psql_config['PASSWORD']}@{psql_config['HOST']}:{psql_config['PORT']}/{psql_config['DATABASE']}"
        self.psql_config["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
        self.mongo_config = mongo_config
        self.psql_db = psql_db
        self.mongo_db = mongo_db

    def connect_databases(self):
        current_app.logger.debug("Connecting databases")
        connected_to = []
        if self.app_config.get("CONNECT_PSQL"):
            current_app.logger.debug("Connecting PSQL")
            self.connect_psql()
            connected_to.append("PSQL")
        if self.app_config.get("CONNECT_MONGO"):
            current_app.logger.debug("Connecting Mongo")
            self.connect_mongo()
            connected_to.append("Mongo")
        current_app.logger.debug(f"Connected to {connected_to}")

    def connect_psql(self):
        session_options = {
            "autocommit": False,
            "autoflush": False,
            "query_cls": SQLQuery,
        }

        def connect():
            try:
                self.psql_db.connect(
                    config=self.psql_config,
                    session_options=session_options,
                    use_scoped=True,
                )
                return True
            except Exception:
                return False

        self.wait_for_service(30, 1, connect, "PSQL")

    def connect_mongo(self):
        def connect():
            try:
                self.mongo_db.connect(config=self.mongo_config)
                return True
            except Exception:
                return False

        self.wait_for_service(30, 1, connect, "MongoDB")

    def cleanup_databases(self, e):
        if self.app_config.get("CONNECT_PSQL"):
            self.cleanup_psql()
        if self.app_config.get("CONNECT_MONGO"):
            self.cleanup_mongo()
        return e

    def cleanup_psql(self):
        self.psql_db.session.remove()

    def cleanup_mongo(self):
        pass

    def wait_for_service(
        self, timeout: int, pause: float, callback, service: str
    ):
        """Wait until postgres service is ready.

        Params
        ------------
        timeout : int
            Seconds to wait for postgres service
        pause : float
            Seconds to wait between checks
        callback : callable
            Callable that performs the check.
            Must return True if service is available.
            Must return False if service is not available.
        """

        def timeout_handler(signum, frame):
            raise Exception(f"Timed out waiting for {service} service")

        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        except ValueError:
            # signal does not work on threads
            pass

        while True:
            conn = callback()
            if conn:
                signal.alarm(0)
                return conn
            time.sleep(pause)
