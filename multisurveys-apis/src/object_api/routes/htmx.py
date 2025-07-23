import os
import pprint
import traceback
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..services.object_services import get_tidy_classifiers


router = APIRouter()
templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8001"
)


@router.get("/form/", response_class=HTMLResponse)
async def objects_form(request: Request):

    try:
        session = request.app.state.psql_session
        classifiers = get_tidy_classifiers(session)

        return templates.TemplateResponse(
        name="form.html.jinja",
        context={
            "request": request,
            "classifiers": classifiers
        }
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")
    


@router.get("/select", response_class=HTMLResponse)
async def select_classes_classifier(
    request: Request,
    classifier_classes: list[str] = Query(...)
    ):

    try:
        classes = classifier_classes

        return templates.TemplateResponse(
        name="dependent_select.html.jinja",
        context={
            "request": request,
            "classes": classes
        }
    )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred")