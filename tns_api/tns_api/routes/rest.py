import traceback
import json
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import Response
from ..services.handle_errors import ObjectNotFound
from ..services.tns_services import get_object_tns, empty_object_dict

router = APIRouter()


@router.get("/")
def root():
    return "this is the tns api"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.post("/search")
async def search(ra: Annotated[float, Body()], dec: Annotated[float, Body()]):
    try:
        response = get_object_tns(ra, dec)

        return Response(content=response, media_type="application/json")
    except ObjectNotFound as e:
        traceback.print_exc()
        response = empty_object_dict()
        return Response(content=response, media_type="application/json")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
