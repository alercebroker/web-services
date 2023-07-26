from pymongo import ASCENDING, IndexModel, MongoClient


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
        self._collections = {
            "detection": {
                "indexes": [
                    IndexModel([("aid", ASCENDING), ("oid", ASCENDING)]),
                    IndexModel([("sid", ASCENDING)]),
                ]
            },
            "non_detection": {
                "indexes": [
                    IndexModel(
                        [
                            ("aid", ASCENDING),
                            ("fid", ASCENDING),
                            ("mjd", ASCENDING),
                        ],
                        name="unique",
                        unique=True,
                    ),
                    IndexModel([("sid", ASCENDING)], name="sid"),
                ]
            },
        }

    def create_database(self):
        db = self.client[self.database_name]
        for c in self._collections:
            collection = db[c]
            collection.create_indexes(self._collections[c]["indexes"])

    def delete_database(self):
        db = self.client[self.database_name]
        self.client.drop_database(db)

    @property
    def database(self):
        return self.client[self.database_name]
