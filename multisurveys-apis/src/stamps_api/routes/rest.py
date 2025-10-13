from fastapi import APIRouter, Request, Response
from ...s3_handler import handler_selector

router = APIRouter()
templates = Jinja2Templates(
    directory="src/multisurvey_stamps/templates", autoescape=True, auto_reload=True
)

router = APIRouter()


@router.get("/")
async def ping():
    return "This is the Stamps API"


@router.get("/stamp")
async def stamp(
    request: Request,
    oid: str,
    measurement_id: str,
    stamp_type: str,
    file_format: str,
    survey_id: str,
):
    handler = handler_selector(survey_id)()

    _, file_buffer, mime = handler.get_stamp(
        oid, measurement_id, stamp_type, file_format
    )

    return Response(content=file_buffer.getvalue(), media_type=mime)


@router.get("/avro")
async def stamp(
    request: Request, oid: str, measurement_id: str, survey_id: str
):
    handler = handler_selector(survey_id)()

    avro_json = handler.get_avro(oid, measurement_id)

    return avro_json

