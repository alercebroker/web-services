
import re
import os
from typing import Annotated
from fastapi import Query
import json
import requests

from core.services.object import get_object
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, HTMLError
from ..result_handler import handle_error, handle_success
from ..get_crossmatch_data import get_alerce_data
router = APIRouter()
templates = Jinja2Templates(
    directory="src/crossmatch_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8005"
)

@router.get("/crossmatch/{oid}", response_class=HTMLResponse)
async def object_xmatch_app(
    request: Request,
    oid: str,
):

    object = get_object(oid,session_factory = request.app.state.psql_session)

    try:
        cross = get_alerce_data(object.meanra, object.meandec, 20)
    except  requests.RequestException as e:
        return HTMLError(e)

    '''
        get_alerce_data returns a list with several dictionaries. The dict format is one key and then a value that is another dictionary.
        Something like:

                    [{'name1': {key1: info1, key2: info2, key3: info3, ...}}, 'name2' : {key4: info4, key5: info5, key6: info7, ...}, ...]

        In the next iteration we want to fill cross_keys with 'name1', 'name2', ... ,i.e., we want to fill cross_keys with the first (and only) key in every dict
        so the approach is to take every dict in the list and then take the first key (and only) in the dictionary with next(iter(...))
    '''

    cross_keys = []
    for i in range(len(cross)):
        cross_keys.append(next(iter(cross[i].keys())))
    
    return templates.TemplateResponse(
      name='crossmatch.html.jinja',
      context={'request': request,
               'cross': cross,
               'crossKeys': cross_keys,
               },
  )