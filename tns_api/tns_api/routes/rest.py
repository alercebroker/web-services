import traceback
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from ..services.tns_services import get_object_tns


router = APIRouter()

@router.get("/")
def root():
    return "this is the tns api"

@router.get("/healthcheck")
def healthcheck():
    return "OK"

@router.post("/search/")
async def search(ra: Annotated[float, Body(gt=0)], dec: Annotated[float, Body(gt=0)]):
    try:
        response = get_object_tns(ra, dec)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")

    return JSONResponse(content=response)