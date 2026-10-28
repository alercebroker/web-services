from fastapi import APIRouter, Depends

from ..models.status import Scenario, Status
from ..services.status import get_status
from .parameters import pipeline_survey, simulation_scenario, since_spans

router = APIRouter()


@router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return "OK"


@router.get(
    "/pipeline_status",
    response_model=Status,
    summary="Is each pipeline up to date, and how many alerts it received and processed",
)
def pipeline_status(
    survey_id: str | None = Depends(pipeline_survey),
    since: list[str] = Depends(since_spans),
    scenario: Scenario | None = Depends(simulation_scenario),
):
    """For each pipeline (`lsst`, `ztf`), or only the `survey_id` one: its status, the alerts waiting, when it last
    received and processed an alert, and the alerts it received and processed in each `since` span.

    Alerts are not objects: an object gets one alert per detection, and processed alerts take a few minutes to
    become searchable. Answers are cached for a short while, so asking very often gives the same answer.
    """
    status = get_status(since, scenario)
    if survey_id is None:
        return status
    return status.model_copy(update={"pipelines": [p for p in status.pipelines if p.survey == survey_id]})
