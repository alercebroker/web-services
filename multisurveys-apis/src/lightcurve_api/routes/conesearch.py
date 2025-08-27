import traceback

import numpy as np
from fastapi import APIRouter, HTTPException

from core.config.dependencies import db_dependency
from core.idmapper.idmapper import decode_masterid

router = APIRouter()


@router.get("/conesearch")
def conesearch(
    oid: int,
    db: db_dependency,
):
    survey, id = decode_masterid(np.int64(oid))
    try:
        return f"{survey} {id}"
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
