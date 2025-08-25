import traceback

from lightcurve_api.services.idmapper.idmapper import decode_masterid
import numpy as np
from fastapi import HTTPException

from .rest import router, db


@router.get("/conesearch")
def conesearch(
    oid: int,
    db: db,
):
    survey, id = decode_masterid(np.int64(oid))
    try:
        pass
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
