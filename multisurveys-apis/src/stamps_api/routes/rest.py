from typing import Literal

from fastapi import APIRouter, Request, Response

from core.idmapper.survey_mapper import Survey
from ..s3_handler import handler_selector

router = APIRouter()


@router.get("/")
def ping():
    return "This is the Stamps API"


@router.get("/stamp")
def stamp(
    request: Request,
    oid: str,
    measurement_id: str,
    stamp_type: Literal["cutoutDifference", "cutoutScience", "cutoutTemplate"],
    file_format: Literal["png", "fits"],
    survey_id: Survey,
    is_compressed: bool = True,
):
    handler = handler_selector(survey_id)()
    _, file_buffer, mime = handler.get_stamp(oid, measurement_id, stamp_type, file_format, is_compressed)

    return Response(content=file_buffer.getvalue(), media_type=mime)


@router.get("/avro")
def avro(request: Request, oid: str, measurement_id: str, survey_id: Survey):
    handler = handler_selector(survey_id)()

    avro_json = handler.get_avro(oid, measurement_id)

    return avro_json
