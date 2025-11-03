from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from core.repository.queries.objects import query_object_by_id
from crossmatch_api.get_crossmatch_data import get_alerce_data

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
    object = query_object_by_id(oid=oid, survey_id=survey_id, session_ms=request.app.state.psql_session)
    object = object[0].__dict__
    cross = get_alerce_data(object["meanra"], object["meandec"], 20)

    return cross
