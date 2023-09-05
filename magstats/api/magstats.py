from fastapi import FastAPI, HTTPException, Path
from sqlalchemy.orm import Session
from api.container import AppContainer
from db_plugins.db.sql import models
from ..core.models import MagstatsModel
from dependency_injector.wiring import inject, Provide

app = FastAPI()

@app.get("/magstats/{id}", response_model= MagstatsModel)
@inject
def get_magstats(
    id: int = Path(..., title="The object's identifier"),
    session: Session = Provide[AppContainer.psql_db.provided.session],
):
    obj = session.query(models.Object).filter(models.Object.oid == id).one_or_none()
    if obj:
        return obj.magstats
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    # en el core se crea la instancia sesion y se le consulta, aca solo se llama al core.
