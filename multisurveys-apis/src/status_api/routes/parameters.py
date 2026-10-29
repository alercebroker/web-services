from fastapi import Query

from core.idmapper.survey_mapper import Survey

from ..models.status import DEFAULT_SINCE, Scenario, Since
from ..settings import PIPELINES, settings


def since_spans(
    since: list[Since] = Query(
        DEFAULT_SINCE,
        description="Time spans to count alerts in. Repeat it to ask for several: `?since=1h&since=24h`.",
    ),
) -> list[str]:
    return list(dict.fromkeys(since))


def simulation_scenario(scenario: Scenario | None = Query(None, include_in_schema=False)) -> Scenario | None:
    """Only for demos with simulated data (PIPELINE_STATUS_SOURCE=fake): ignored otherwise, so not in /docs."""
    return scenario if settings.source == "fake" else None


def pipeline_survey(
    survey_id: Survey | None = Query(
        None, description="Only this survey's pipeline: `ztf` or `lsst` (case-insensitive)."
    ),
) -> str | None:
    if survey_id is not None and survey_id not in [p.id for p in PIPELINES]:
        raise ValueError(f"No pipeline status for survey: {survey_id}")
    return survey_id
