import signal
import time
from db_plugins.db.sql.connection import SQLConnection, SQLQuery
from db_plugins.db.mongo.connection import MongoConnection
from flask import current_app


class DBControl(object):

    # Initialization and cleanup methods
    def __init__(
        self,
        mongo_config: dict,
        mongo_db: MongoConnection,
    ) -> None:
        self.mongo_config = mongo_config
        self.mongo_db = mongo_db

    def connect_databases(self):
        current_app.logger.debug("Connecting database")
        current_app.logger.debug("Connecting Mongo")
        self.connect_mongo()
        current_app.logger.debug(f"Connected to Mongo")

    def connect_mongo(self):
        def connect():
            try:
                self.mongo_db.connect(config=self.mongo_config)
                return True
            except Exception:
                return False

        self.wait_for_service(30, 1, connect, "MongoDB")

    def cleanup_databases(self, e):
        return e

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
