import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.repository.queries.objects import (
    query_object_by_id,
)
from crossmatch_api.get_crossmatch_data import get_alerce_data

router = APIRouter()
templates = Jinja2Templates(directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True)
templates.env.globals["API_URL"] = os.getenv("API_URL", "http://localhost:8005")


@router.get("/htmx/crossmatch", response_class=HTMLResponse)
async def object_mag_app(request: Request, oid: str, survey_id: str):
    object = query_object_by_id(oid=oid, survey_id=survey_id, session_ms=request.app.state.psql_session)
    object = object[0].__dict__
    cross = get_alerce_data(object["ra"], object["dec"], 20)

    """
        get_alerce_data returns a list with several dictionaries. The dict format is one key and then a value that is another dictionary.
        Something like:

                    [{'name1': {key1: info1, key2: info2, key3: info3, ...}}, 'name2' : {key4: info4, key5: info5, key6: info7, ...}, ...]

        In the next iteration we want to fill cross_keys with 'name1', 'name2', ... ,i.e., we want to fill cross_keys with the first (and only) key in every dict
        so the approach is to take every dict in the list and then take the first key (and only) in the dictionary with next(iter(...))
    """

    cross_keys = []
    for i in range(len(cross)):
        cross_keys.append(next(iter(cross[i].keys())))

    return templates.TemplateResponse(
        name="crossmatch.html.jinja",
        context={
            "request": request,
            "cross": cross,
            "crossKeys": cross_keys,
        },
    )
