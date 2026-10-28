from fastapi import APIRouter, HTTPException, Request, Response

from core.idmapper.survey_mapper import Survey
from ..s3_handler import handler_selector

router = APIRouter()

FILE_FORMATS = ("png", "fits")


@router.get("/")
def ping():
    return "This is the Stamps API"


@router.get("/stamp")
def stamp(
    request: Request,
    oid: str,
    measurement_id: str,
    stamp_type: str,
    file_format: str,
    survey_id: Survey,
    is_compressed: bool = True,
):
    handler = handler_selector(survey_id)()
    # Validate before the S3 download, so bad input fails fast
    if stamp_type not in handler.valid_stamp_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stamp_type '{stamp_type}'. Valid types are {handler.valid_stamp_types}",
        )
    if file_format not in FILE_FORMATS:
        raise HTTPException(status_code=400, detail=f"Invalid file_format '{file_format}'. Use png or fits.")
    _, file_buffer, mime = handler.get_stamp(oid, measurement_id, stamp_type, file_format, is_compressed)

    return Response(content=file_buffer.getvalue(), media_type=mime)


@router.get("/avro")
def avro(request: Request, oid: str, measurement_id: str, survey_id: Survey):
    handler = handler_selector(survey_id)()

    avro_json = handler.get_avro(oid, measurement_id)

    return avro_json
