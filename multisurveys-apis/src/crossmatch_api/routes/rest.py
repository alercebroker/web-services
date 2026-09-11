from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..services.crossmatch_service import get_cross_data
from ..models.object import ObjectInformation

router = APIRouter()
templates = Jinja2Templates(directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True)


@router.get("/")
def root():
    return "This is the crossmatch API"


@router.get("/healthcheck")
def healthcheck():
    return "OK"


@router.get("/crossmatch")
async def object_mag_app(request: Request, oid: str, survey_id: str):
    session = request.app.state.psql_session

    object_details = ObjectInformation(oid=oid, survey=survey_id)

    cross = get_cross_data(object_details, session)

    return cross
