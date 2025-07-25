import os
import pprint
import traceback
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..services.object_services import get_tidy_classifiers
from ..models.filters import Consearch, Filters, SearchParams
from ..models.pagination import Order, PaginationArgs
from ..services.object_services import get_objects_list
from ..services.validations import ndets_validation, order_mode_validation
from ..services.jinja_tools import truncate_float


router = APIRouter()

templates = Jinja2Templates(
    directory="src/object_api/templates", autoescape=True, auto_reload=True
)
templates.env.globals["API_URL"] = os.getenv(
    "API_URL", "http://localhost:8001"
)

templates.env.filters['truncate'] = truncate_float


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
    

@router.get("/table", response_class=HTMLResponse)
def objects_table(
    request: Request,
    class_name: str | None = None,
    oid: Annotated[list[str] | None, Query()] = None,
    survey: str | None = None,
    classifier: str | None = Query(default="lc_classifier"),
    ranking: int | None = Query(default=1),
    n_det: Annotated[list[int] | None, Query()] = None,
    probability: float | None = Query(default=0),
    firstmjd: Annotated[list[float] | None, Query()] = None,
    lastmjd: Annotated[list[float] | None, Query()] = None,
    dec: float | None = None,
    ra: float | None = None,
    radius: float | None = None,
    page: int | None = 1,
    page_size: int | None = 10,
    count: bool | None = False,
    order_by: str | None = Query(default="probability"),
    order_mode: str | None = Query(default="DESC"),
):
    try:
        session = request.app.state.psql_session
        
        ndets_validation(n_det)
        order_mode_validation(order_mode)

        filters = Filters(
            oids=oid,
            survey = survey,
            classifier=classifier,
            class_name=class_name,
            ranking=ranking,
            n_det=n_det,
            probability=probability,
            firstmjd=firstmjd,
            lastmjd=lastmjd,
        )

        conesearch = Consearch(dec=dec, ra=ra, radius=radius)

        pagination = PaginationArgs(page=page, page_size=page_size, count=count)

        order = Order(order_by=order_by, order_mode=order_mode)

        search_params = SearchParams(
            filter_args=filters,
            conesearch_args=conesearch,
            pagination_args=pagination,
            order_args=order,
        )

        object_list = get_objects_list(
            session_ms=session, search_params=search_params
        )

        return templates.TemplateResponse(
            name="objects_table.html.jinja",
            context={
                "request": request,
                "objects_list": object_list
            }
        )
    except HTTPException as e:
        traceback.print_exc()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred")
