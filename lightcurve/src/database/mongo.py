from pymongo import MongoClient


class MongoDatabase:
    def __init__(self, config=None):
        """
        Establishes connection to a database and initializes a session.

        Parameters
        ----------
        config : dict
            Database configuration. For example:

            .. code-block:: python

                config = {
                    "host": "host",
                    "username": "username",
                    "password": "pwd",
                    "port": "27017", # mongo typically runs on port 27017.
                    "database": "database",
                    "authSource": admin" # could be admin or the same as DATABASE
                }
        """
        self._config = config
        self.database_name = config.pop("database")
        self.client = MongoClient(**self._config)

    @property
    def database(self):
        return self.client[self.database_name]
