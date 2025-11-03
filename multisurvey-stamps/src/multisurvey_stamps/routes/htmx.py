from fastapi import APIRouter, Request
from fastapi import Response
from ...s3_handler import handler_selector


router = APIRouter()


@router.get("/stamp_card")
async def stamp_card(
    request: Request, oid: str, measurement_id: str, survey_id: str
):
    handler = handler_selector(survey_id)()

    stamps = handler.get_all_stamps(oid, measurement_id, "png")

    return Response()
