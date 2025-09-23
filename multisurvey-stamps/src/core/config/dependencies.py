from typing import Annotated
from db_plugins.db.sql._connection import PsqlDatabase
from fastapi import Depends
from .connection import ApiDatabase

db_dependency = Annotated[PsqlDatabase, Depends(ApiDatabase)]
