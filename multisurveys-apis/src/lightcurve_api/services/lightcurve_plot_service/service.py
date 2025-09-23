import copy
import csv
import io
import zipfile
from collections import defaultdict
from itertools import chain
from typing import Callable, ContextManager, List

import httpx
from sqlalchemy.orm.session import Session
from toolz import curry, pipe, reduce

from lightcurve_api.models.detections import LsstDetection, ztfDetection
from lightcurve_api.models.force_photometry import LsstForcedPhotometry, ZtfForcedPhotometry
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.lightcurve_item import (
    BaseDetection,
    BaseForcedPhotometry,
    BaseNonDetection,
)
from lightcurve_api.models.non_detections import ZtfNonDetections
from lightcurve_api.routes.htmx.parsers import ConfigState
from lightcurve_api.services.parsers import parse_ztf_dr_detection, parse_ztf_dr_object
from lightcurve_api.services.period.service import get_period

from ..conesearch.conesearch import conesearch_oid_lightcurve
from .chart_point import ChartPoint
from .result import Result

DEFAULT_RADIUS = 30 / 3600
DEFAULT_NEIGHBORS = 2
DETECTION = "det"
NON_DETECTION = "lim. mag"
FORCED_PHOTOMETRY = "f. phot"
ZTF_SURVEY = "ztf"
LSST_SURVEY = "lsst"
ZTF_DR_SURVEY = "ztf dr"
COLORS = {
    ZTF_SURVEY: {"g": "#56E03A", "r": "#D42F4B", "i": "#F4D617"},
    LSST_SURVEY: {"u": "#1600EA", "g": "#31DE1F", "r": "#B52626", "i": "#370201", "z": "#BA52FF", "y": "#61A2B3"},
    ZTF_DR_SURVEY: {"g": "#ADA3A3", "r": "#377EB8", "i": "#FF7F00"},
}
SYMBOLS = {
    ZTF_SURVEY: {DETECTION: "circle", NON_DETECTION: "triangle", FORCED_PHOTOMETRY: "rect"},
    LSST_SURVEY: {DETECTION: "roundRect", NON_DETECTION: "diamond", FORCED_PHOTOMETRY: "arrow"},
    ZTF_DR_SURVEY: {DETECTION: "circle", NON_DETECTION: "triangle", FORCED_PHOTOMETRY: "rect"},
}
OFFSETS = {
    "g": 1,
    "r": 2,
    "i": 3,
    "u": 4,
    "z": 5,
    "y": 6,
}


def create_series(name: str, survey: str, band: str, data: List[List[float]], offset: bool) -> dict:
    series_name = name + " " + survey.upper() + ": " + band
    return {
        "name": series_name + " *" + str(OFFSETS[band]) if offset else series_name,
        "type": "scatter",
        "data": data,
        "color": COLORS[survey][band],
        "symbol": SYMBOLS[survey][name],
    }


def create_error_bar_series(name: str, survey: str, band: str, data: List[List[float]], offset: bool):
    series_name = name + " " + survey.upper() + ": " + band
    return {
        "name": series_name + " *" + str(OFFSETS[band]) if offset else series_name,
        "type": "custom",
        "data": data,
        "color": COLORS[survey][band],
        "renderItem": "renderError",
        "scale": True,
    }


def default_echarts_options(config_state: ConfigState):
    return {
        "tooltip": {},
        "grid": {"right": "25%", "left": "5%", "bottom": "7%", "top": "10%"},
        "legend": {
            "right": 10,
            "top": 80,
            "orient": "vertical",
            "selectedMode": False,
            "itemWidth": 15,
        },
        "xAxis": {"type": "value", "name": "MJD", "scale": True, "splitLine": False},
        "yAxis": {
            "type": "value",
            "name": "Magnitude",
            "scale": True,
            "inverse": not config_state.flux,
            "nameLocation": "start",
            "splitLine": False,
        },
        "series": [],
        "animation": False,
    }


def lightcurve_plot(oid: str, survey_id: str, session_factory: Callable[..., ContextManager[Session]]) -> Result:
    result = Result({}, Lightcurve(detections=[], non_detections=[], forced_photometry=[]), config_state=ConfigState())
    return pipe(
        get_lightcurve(result, oid, survey_id, session_factory),
        set_default_echart_options,
        calculate_period,
        set_chart_options_detections,
        set_chart_options_non_detections,
        set_chart_options_forced_photometry,
    )


def update_lightcurve_plot(
    config_state: ConfigState,
    detections: List[BaseDetection],
    non_detections: List[BaseNonDetection],
    forced_photometry: List[BaseForcedPhotometry],
) -> Result:
    return pipe(
        Result(
            {},
            Lightcurve(detections=detections, non_detections=non_detections, forced_photometry=forced_photometry),
            config_state=validate_config_state(config_state),
        ),
        set_default_echart_options,
        set_chart_options_external_sources,
        set_chart_options_detections,
        set_chart_options_non_detections,
        set_chart_options_forced_photometry,
    )


def validate_config_state(config_state: ConfigState) -> ConfigState:
    config_state = config_state.model_copy(deep=True)

    if config_state.external_sources.enabled:
        config_state.total = True

    if config_state.fold:
        config_state.total = True

    return config_state


def get_lightcurve(result: Result, oid: str, survey_id: str, session_factory: Callable[..., ContextManager[Session]]):
    return Result(
        copy.deepcopy(result.echart_options),
        conesearch_oid_lightcurve(
            oid,
            DEFAULT_RADIUS,
            DEFAULT_NEIGHBORS,
            survey_id,
            session_factory,
        ),
        config_state=result.config_state.model_copy(deep=True),
    )


def set_default_echart_options(result: Result) -> Result:
    result_copy = result.copy()
    chart_options = default_echarts_options(result.config_state)
    result_copy.echart_options = chart_options
    return result_copy


def set_chart_options_detections(result: Result) -> Result:
    result_copy = result.copy()

    # Chart points
    pipe(
        result_copy.lightcurve.detections,
        curry(create_chart_detections, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=False, config_state=result.config_state),
        curry(_transform_to_series, series_type=DETECTION, offset_bands=result.config_state.offset_bands),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.detections,
        curry(create_chart_detections, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=True, config_state=result.config_state),
        curry(
            _transform_to_series, series_type=DETECTION, offset_bands=result.config_state.offset_bands, error_bar=True
        ),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    return result_copy


def set_chart_options_non_detections(result: Result) -> Result:
    result_copy = result.copy()

    if result.config_state.total:
        return result_copy

    series = pipe(
        result_copy.lightcurve.non_detections,
        curry(create_chart_non_detections, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=False, config_state=result.config_state),
        curry(_transform_to_series, series_type=NON_DETECTION, offset_bands=result.config_state.offset_bands),
    )

    result_copy.echart_options["series"].extend(series)
    return result_copy


def set_chart_options_forced_photometry(result: Result) -> Result:
    result_copy = result.copy()

    # Chart points
    pipe(
        result_copy.lightcurve.forced_photometry,
        curry(create_chart_forced_photometry, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=False, config_state=result.config_state),
        curry(_transform_to_series, series_type=FORCED_PHOTOMETRY, offset_bands=result.config_state.offset_bands),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.forced_photometry,
        curry(create_chart_forced_photometry, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=True, config_state=result.config_state),
        curry(
            _transform_to_series,
            series_type=FORCED_PHOTOMETRY,
            offset_bands=result.config_state.offset_bands,
            error_bar=True,
        ),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    return result_copy


def create_chart_detections(detections: List[BaseDetection], config_state: ConfigState) -> List[ChartPoint]:
    result: list[ChartPoint] = []
    for det in detections:
        if (
            det.survey_id.lower() == ZTF_SURVEY or det.survey_id.lower() == ZTF_DR_SURVEY
        ) and det.band_name() not in config_state.bands.ztf:
            continue
        if det.survey_id.lower() == LSST_SURVEY and det.band_name() not in config_state.bands.lsst:
            continue

        result.append(
            ChartPoint(
                det.survey_id,
                det.band_name(),
                det.phase(config_state.period) if config_state.fold else det.mjd,
                det.magnitude2flux(config_state.total) if config_state.flux else det.flux2magnitude(config_state.total),
                det.magnitude2flux_err(config_state.total)
                if config_state.flux
                else det.flux2magnitude_err(config_state.total),
            )
        )

    # Add second phase, repeating the same points when folding
    if config_state.fold:
        result.extend([ChartPoint(point.survey, point.band, point.x + 1, point.y, point.error) for point in result])

    return result


def create_chart_non_detections(non_detections: List[BaseNonDetection], config_state: ConfigState) -> List[ChartPoint]:
    result = []
    if config_state.fold:
        return result

    for ndet in non_detections:
        if ndet.survey_id.lower() == ZTF_SURVEY and ndet.band_name() not in config_state.bands.ztf:
            continue

        result.append(ChartPoint(ndet.survey_id, ndet.band_name(), ndet.mjd, ndet.get_mag(), 0))

    return result


def create_chart_forced_photometry(
    forced_photometry: List[BaseForcedPhotometry], config_state: ConfigState
) -> List[ChartPoint]:
    result = []

    for fphot in forced_photometry:
        if fphot.survey_id.lower() == LSST_SURVEY and fphot.band_name() not in config_state.bands.lsst:
            continue
        if fphot.survey_id.lower() == ZTF_SURVEY and fphot.band_name() not in config_state.bands.ztf:
            continue

        result.append(
            ChartPoint(
                fphot.survey_id,
                fphot.band_name(),
                fphot.phase(config_state.period) if config_state.fold else fphot.mjd,
                fphot.magnitude2flux(config_state.total)
                if config_state.flux
                else fphot.flux2magnitude(config_state.total),
                fphot.magnitude2flux_err(config_state.total)
                if config_state.flux
                else fphot.flux2magnitude_err(config_state.total),
            )
        )
    if config_state.fold:
        result.extend([ChartPoint(point.survey, point.band, point.x + 1, point.y, point.error) for point in result])

    return result


def set_chart_options_external_sources(result: Result) -> Result:
    result_copy = result.copy()

    if len(result_copy.lightcurve.detections) == 0 or not result.config_state.external_sources.enabled:
        return result_copy

    meanra = sum(det.ra for det in result.lightcurve.detections) / len(result.lightcurve.detections)
    meandec = sum(det.dec for det in result.lightcurve.detections) / len(result.lightcurve.detections)

    meanra = 269.0062838  # TODO: TEST COORDINATES
    meandec = -16.4499040  # TODO: TEST COORDINATES
    with httpx.Client() as client:
        result_copy.lightcurve.detections.extend(
            pipe(
                client.get(
                    "https://api.alerce.online/ztf/dr/v1/light_curve/",
                    params={"ra": meanra, "dec": meandec, "radius": 1.5},
                ).json(),
                curry(
                    parse_ztf_dr_detection,
                    object_ids=result_copy.config_state.external_sources.selected_objects,
                ),
            )
        )
    return result_copy


def calculate_period(result: Result) -> Result:
    result_copy = result.copy()
    result_copy.config_state.period = get_period(result.lightcurve.detections)
    return result_copy


def get_ztf_dr_objects(
    config_state: ConfigState,
    detections: list[BaseDetection],
    non_detections: list[BaseNonDetection],
    forced_photometry: list[BaseForcedPhotometry],
) -> Result:
    result = Result(
        {},
        Lightcurve(detections=detections, non_detections=non_detections, forced_photometry=forced_photometry),
        config_state=validate_config_state(config_state),
    )

    if len(result.lightcurve.detections) == 0:
        return result

    meanra = sum(det.ra for det in result.lightcurve.detections) / len(result.lightcurve.detections)
    meandec = sum(det.dec for det in result.lightcurve.detections) / len(result.lightcurve.detections)

    meanra = 269.0062838  # TODO: TEST COORDINATES
    meandec = -16.4499040  # TODO: TEST COORDINATES
    with httpx.Client() as client:
        result.config_state.external_sources.objects.extend(
            pipe(
                client.get(
                    "https://api.alerce.online/ztf/dr/v1/light_curve/",
                    params={"ra": meanra, "dec": meandec, "radius": 1.5},
                ).json(),
                parse_ztf_dr_object,
            )
        )
    return result


def _group_chart_points_by_survey_band(chart_points: List[ChartPoint], config_state: ConfigState, error_bar=False):
    """Group chart points by survey and band in a functional style."""

    def _add_point_to_group(group: dict, point: ChartPoint):
        limit = 99999 if config_state.flux else 1
        point_value = point.point() if not error_bar else point.error_bar(limit)
        group[point.survey][point.band].append(point_value)
        return group

    return reduce(_add_point_to_group, chart_points, defaultdict(lambda: defaultdict(list)))


def _transform_to_series(
    grouped_data: dict[str, dict[str, List[List[float]]]], series_type: str, offset_bands: bool, error_bar=False
) -> List[dict]:
    """Transform grouped data into series with optional band offsetting."""

    def _create_series_for_band(survey_band_data: tuple[str, dict[str, List[List[float]]]]):
        survey, bands_data = survey_band_data

        def _process_band(band_data: tuple[str, List[List[float]]]):
            band, data = band_data

            if offset_bands:
                data = [[d[0], d[1] * OFFSETS[band]] for d in data]

            return (
                create_series(series_type, survey, band, data, offset_bands)
                if not error_bar
                else create_error_bar_series(series_type, survey, band, data, offset_bands)
            )

        return map(_process_band, bands_data.items())

    # Flatten the nested structure into a single list of series
    return list(chain.from_iterable(map(_create_series_for_band, grouped_data.items())))


def _data_to_csv(data_list, fieldnames: set):
    """Convert a list of Pydantic models to CSV format"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in data_list:
        writer.writerow(item.model_dump())
    return output.getvalue()


def zip_lightcurve(detections, non_detections, forced_photometry):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if detections:
            detections_csv = _data_to_csv(
                detections, set(list(ztfDetection.model_fields.keys()) + list(LsstDetection.model_fields.keys()))
            )
            zip_file.writestr("detections.csv", detections_csv)

        if non_detections:
            non_detections_csv = _data_to_csv(non_detections, set(list(ZtfNonDetections.model_fields.keys())))
            zip_file.writestr("non_detections.csv", non_detections_csv)

        if forced_photometry:
            forced_photometry_csv = _data_to_csv(
                forced_photometry,
                set(list(ZtfForcedPhotometry.model_fields.keys()) + list(LsstForcedPhotometry.model_fields.keys())),
            )
            zip_file.writestr("forced_photometry.csv", forced_photometry_csv)

    zip_buffer.seek(0)
    return zip_buffer
