from dependency_injector import containers, providers
from db_plugins.db.sql.connection import SQLConnection, SQLQuery
from db_plugins.db.mongo.connection import MongoConnection
from core.light_curve.container import LightcurveContainer
from shared.database.control import DBControl


session_options = {
    "autocommit": False,
    "autoflush": False,
    "query_cls": SQLQuery,
}


class AppContainer(containers.DeclarativeContainer):
    # config
    config = providers.Configuration(yaml_files=["config.yml"])

    # gateways
    psql_db = providers.Singleton(SQLConnection)
    mongo_db = providers.Singleton(MongoConnection)
    database_config = config.DATABASE
    SQLALCHEMY_DATABASE_URL = f"postgresql://{database_config.SQL.USER}:{database_config.SQL.PASSWORD}@{database_config.SQL.HOST}:{database_config.SQL.PORT}/{database_config.SQL.DATABASE}"
    database_config.SQL.SQLALCHEMY_DATABASE_URL.from_value(
        SQLALCHEMY_DATABASE_URL
    )
    db_control = providers.Singleton(
        DBControl,
        app_config=database_config.APP_CONFIG,
        psql_config=database_config.SQL,
        mongo_config=database_config.MONGO,
        psql_db=psql_db,
        monge_db=mongo_db,
    )

    # packages
    lightcurve_package = providers.Container(
        LightcurveContainer, psql_db=psql_db, mongo_db=mongo_db
    )
