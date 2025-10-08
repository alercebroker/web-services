from typing import Annotated

from crossmatch_api.services.xwave_service.service import ConesearchQuery
from db_plugins.db.sql._connection import PsqlDatabase
from fastapi import Depends

from crossmatch_api.services.xwave_client import client

from .connection import ApiDatabase

db_dependency = Annotated[PsqlDatabase, Depends(ApiDatabase)]
xwave_conesearch_dependency = Annotated[ConesearchQuery, Depends(lambda: client.conesearch)]
