from .psql_db import db as psql_db, session_options
from .mongo_db import db as mongo_db
import signal
import time


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
        def connect():
            try:
                psql_db.connect(
                    config=self.psql_config,
                    session_options=session_options,
                    use_scoped=True,
                )
                return True
            except Exception:
                return False

        self.wait_for_service(30, 1, connect)

    def connect_mongo(self):
        def connect():
            try:
                mongo_db.connect(config=self.mongo_config)
                return True
            except Exception:
                return False

        self.wait_for_service(30, 1, connect)

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

    def wait_for_service(self, timeout: int, pause: float, callback):
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
            raise Exception("Timed out waiting for postgres service")

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
