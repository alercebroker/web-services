from db_plugins.db.mongo.connection import MongoConnection


class Database:

    def __init__(self, db_config: dict) -> None:
        self.mongo_db = MongoConnection()
        self.mongo_db.connect(db_config)
