import array
import copy
import csv
import io
from os import name
import re
import zipfile
from core.repository.queries.objects import query_object_by_id
import lightcurve_api.services.lightcurve_plot_service.plots_utils as plots_utils
from collections import defaultdict
from itertools import chain
from typing import Callable, ContextManager, List, Dict, Any, Tuple

import httpx
from lightcurve_api.models.periodogram import Periodogram
from lightcurve_api.services.lightcurve_plot_service import plots_utils
from pydantic.networks import MAX_EMAIL_LENGTH
from sqlalchemy import true
from sqlalchemy.orm.session import Session
from toolz import curry, pipe, reduce

from lightcurve_api.models.detections import LsstDetection, ztfDetection
from lightcurve_api.models.force_photometry import (
    LsstForcedPhotometry,
    ZtfForcedPhotometry,
)
from lightcurve_api.models.lightcurve import Lightcurve
from lightcurve_api.models.lightcurve_item import (
    BaseDetection,
    BaseForcedPhotometry,
    BaseNonDetection,
)
from lightcurve_api.models.non_detections import ZtfNonDetections
from lightcurve_api.routes.htmx.parsers import ConfigState
from lightcurve_api.services.parsers import parse_ztf_dr_detection, parse_ztf_dr_object, _parse_object_common
from lightcurve_api.services.period.service import compute_periodogram

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
EMPTY = 'empty'
COLORS = {
    ZTF_SURVEY: {"g": "#56E03A", "r": "#D42F4B", "i": "#F4D617"},
    LSST_SURVEY: {
        "u": "#56B4E9", # sky blue
        "g": "#009E73", # bluish green
        "r": "#D55E00", # vermillion
        "i": "#E69F00", # orange
        "z": "#CC79A7", # reddish purple
        "y": "#0072B2", # blue
    },
    ZTF_DR_SURVEY: {"g": "#ADA3A3", "r": "#377EB8", "i": "#FF7F00"},
    EMPTY: {"empty" : "#00CBFF"}
}
SYMBOLS = {
    ZTF_SURVEY: {
        DETECTION: {"symbol": "circle"},
        NON_DETECTION: {
            "symbol": "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z",
        },
        FORCED_PHOTOMETRY: {"symbol": "square"},
    },
    LSST_SURVEY: {
        DETECTION: {"symbol": "diamond"},
        FORCED_PHOTOMETRY: {"symbol": "pin"},
    },
    ZTF_DR_SURVEY: {
        DETECTION: {"symbol": "circle"},
        NON_DETECTION: {
            "symbol": "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z"
        },
        FORCED_PHOTOMETRY: {"symbol": "square"},
    },
    EMPTY: {
        EMPTY: {"symbol": "none"}
    },
}


def create_series(name: str, survey: str, band: str, data: List[List[float]]) -> dict:
    return {
        "name": name + " " + survey.upper() + ": " + band,
        "type": "scatter",
        "data": data,
        "color": COLORS[survey][band],
        "symbol": SYMBOLS[survey][name]["symbol"],
        "symbolSize": 9,
        "survey": survey,
        "band": band,
    }

def create_error_bar_series(name: str, survey: str, band: str, data: List[List[float]]):
    min_plot_error, max_plot_error = _get_min_and_max_error_bar(data)

    return {
        "name": name + " " + survey.upper() + ": " + band,
        "type": "scatter",
        "data": list(map(lambda point: [point[0], (point[1] + point[2]) / 2], data)),
        "silent": True,
        "symbolSize": 0,
        "color": COLORS[survey][band],
        "markLine": {
            "data": list(
                map(
                    lambda point: [
                        {"coord": [point[0], point[1]], "symbol": "none"},
                        {"coord": [point[0], point[2]], "symbol": "none"},
                    ],
                    data,
                )
            ),
            "lineStyle": {"color": COLORS[survey][band], "type": "solid"},
        },
        "scale": True,
        "survey": survey,
        "band": band,
        "error_bar": True,
        "min_plot_error": min_plot_error,
        "max_plot_error": max_plot_error,
    }

def _get_min_and_max_error_bar(data: List[List[float]]):
    min_plot_error = []
    max_plot_error = []

    for error_bar in data:
        min_ = min(error_bar[1],error_bar[2])
        max_ = max(error_bar[1],error_bar[2])
        mjd = error_bar[0]

        if len(min_plot_error) == 0 and len(max_plot_error) == 0:
            min_plot_error.append(error_bar[0])
            min_plot_error.append(min_)
            max_plot_error.append(error_bar[0])
            max_plot_error.append(max_)
            continue
        

        if min_ < min_plot_error[1]:
            min_plot_error[1] = min_
            min_plot_error[0] = mjd 

        if max_ > max_plot_error[1]:
            max_plot_error[1] = max_
            max_plot_error[0] = mjd
    
    
    return min_plot_error, max_plot_error


def default_echarts_legend(config_state: ConfigState):
    legend = {
        "left": "right",
        "top": "middle",
        "height": "80%",
        "orient": "vertical",
        "selectedMode": False,
        "itemWidth": 20,
        "data": [
            {"name": f"{DETECTION} {ZTF_SURVEY.upper()}: g"},
            {"name": f"{DETECTION} {ZTF_SURVEY.upper()}: r"},
            {"name": f"{DETECTION} {ZTF_SURVEY.upper()}: i"},
            {"name": f"{NON_DETECTION} {ZTF_SURVEY.upper()}: g"},
            {"name": f"{NON_DETECTION} {ZTF_SURVEY.upper()}: r"},
            {"name": f"{NON_DETECTION} {ZTF_SURVEY.upper()}: i"},
            {"name": f"{FORCED_PHOTOMETRY} {ZTF_SURVEY.upper()}: g"},
            {"name": f"{FORCED_PHOTOMETRY} {ZTF_SURVEY.upper()}: r"},
            {"name": f"{FORCED_PHOTOMETRY} {ZTF_SURVEY.upper()}: i"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: u"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: g"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: r"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: i"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: z"},
            {"name": f"{DETECTION} {LSST_SURVEY.upper()}: y"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: u"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: g"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: r"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: i"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: z"},
            {"name": f"{FORCED_PHOTOMETRY} {LSST_SURVEY.upper()}: y"},
            {"name": f"{DETECTION} {ZTF_DR_SURVEY.upper()}: g"},
            {"name": f"{DETECTION} {ZTF_DR_SURVEY.upper()}: r"},
            {"name": f"{DETECTION} {ZTF_DR_SURVEY.upper()}: i"},
        ],
    }
    if config_state.offset_bands:
        # When offset bands are enabled, the legend is inherited from the series data
        legend["data"] = None

    return legend


def default_echarts_options(config_state: ConfigState):
    y_axis_name_location = "start" if not config_state.flux else "end"
    y_axis_name = "Magnitude" if not config_state.flux else "Flux [nJy]"
    return {
        "title": {"show": True, "text": config_state.oid},
        "tooltip": {},
        "grid": {"left": "left", "top": "10%", "width": "75%", "height": "100%"},
        "legend": default_echarts_legend(config_state),
        "xAxis": {"type": "value", "name": "MJD", "scale": True, "splitLine": False},
        "yAxis": {
            "type": "value",
            "name": y_axis_name,
            "scale": True,
            "inverse": not config_state.flux,
            "nameLocation": y_axis_name_location,
            "splitLine": False,
        },
        "series": [],
        "animation": False,
        "toolbox": {
            "show": True,
            "orient": "horizontal",
            "feature": {
                "dataZoom": {"show": True},
                "dataView": {"show": True},
                "saveAsImage": {"show": True},
            },
        },
    }


def lightcurve_plot(oid: str, survey_id: str, session_factory: Callable[..., ContextManager[Session]]) -> Result:
    result = Result(
        {},
        Lightcurve(detections=[], non_detections=[], forced_photometry=[]),
        config_state=ConfigState(oid=oid, survey_id=survey_id),
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
    )
    return pipe(
        get_lightcurve(result, oid, survey_id, session_factory),
        lambda r: get_object_coordinates(r, session_factory=session_factory),
        compute_periodogram,
        set_default_echart_options,
        set_chart_options_detections,
        set_chart_options_non_detections,
        set_chart_options_forced_photometry,
        offset_bands,
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
            Lightcurve(
                detections=detections,
                non_detections=non_detections,
                forced_photometry=forced_photometry,
            ),
            config_state=validate_config_state(config_state),
            periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
        ),
        compute_periodogram,
        set_default_echart_options,
        set_chart_options_external_sources,
        set_chart_options_detections,
        set_chart_options_non_detections,
        set_chart_options_forced_photometry,
        offset_bands,
    )


def validate_config_state(config_state: ConfigState) -> ConfigState:
    config_state = config_state.model_copy(deep=True)

    if config_state.external_sources.enabled:
        config_state.total = True

    if config_state.fold:
        config_state.total = True

    return config_state


def get_lightcurve(
    result: Result,
    oid: str,
    survey_id: str,
    session_factory: Callable[..., ContextManager[Session]],
):
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
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
    )

def get_object_coordinates(result: Result, session_factory: Callable[..., ContextManager[Session]]) -> Result:
    result_copy = result.copy()
    
    object = query_object_by_id(session_factory, result_copy.config_state.oid, result_copy.config_state.survey_id)
    object_model = _parse_object_common(object)

    result_copy.config_state.meanra = object_model.meanra
    result_copy.config_state.meandec = object_model.meandec

    return result_copy


def set_default_echart_options(result: Result) -> Result:
    result_copy = result.copy()
    chart_options = default_echarts_options(result.config_state)
    result_copy.echart_options = chart_options
    return result_copy

def set_chart_options_detections(result: Result) -> Result:
    if "detections" not in result.config_state.data_types:
        return result

    result_copy = result.copy()

    # Chart points
    pipe(
        result_copy.lightcurve.detections,
        curry(create_chart_detections, config_state=result.config_state),
        curry(
            _group_chart_points_by_survey_band,
            error_bar=False,
            config_state=result.config_state,
        ),
        curry(_transform_to_series, series_type=DETECTION),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.detections,
        curry(create_chart_detections, config_state=result.config_state),
        curry(
            _group_chart_points_by_survey_band,
            error_bar=True,
            config_state=result.config_state,
        ),
        curry(_transform_to_series, series_type=DETECTION, error_bar=True),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    #limits of detections errors
    pipe(
        result_copy.echart_options,
        curry(_find_chart_min_and_max_limits, config_state=result.config_state),
        lambda limits_arr: create_series(name='empty', survey='empty', band='empty', data=limits_arr),
        lambda series_dict: [series_dict],
        lambda series: result_copy.echart_options["series"].extend(series),
    )
        
    return result_copy


def _find_chart_min_and_max_limits(echarts_options: dict[str, Any], config_state: ConfigState) -> List:
    if plots_utils._check_limits_conditions(config_state):
        limits_error_plots_arr = _get_min_and_max_errors(echarts_options)

        return limits_error_plots_arr
    
    return []


def _get_min_and_max_errors(echarts_options: dict[str, Any]) -> List:
    limits_error_plots_series = []

    for serie in echarts_options['series']:
        if 'error_bar' in serie:
            limits_error_plots_series.append(serie['min_plot_error'])
            limits_error_plots_series.append(serie['max_plot_error'])

    if not limits_error_plots_series:
        raise ValueError("No error bars found in any series")

    return limits_error_plots_series


def set_chart_options_non_detections(result: Result) -> Result:
    if "non_detections" not in result.config_state.data_types:
        return result

    result_copy = result.copy()

    if result.config_state.total:
        return result_copy

    series = pipe(
        result_copy.lightcurve.non_detections,
        curry(create_chart_non_detections, config_state=result.config_state),
        curry(
            _group_chart_points_by_survey_band,
            error_bar=False,
            config_state=result.config_state,
        ),
        curry(_transform_to_series, series_type=NON_DETECTION),
    )

    result_copy.echart_options["series"].extend(series)
    return result_copy


def set_chart_options_forced_photometry(result: Result) -> Result:
    if "forced_photometry" not in result.config_state.data_types:
        return result

    result_copy = result.copy()

    # Chart points
    pipe(
        result_copy.lightcurve.forced_photometry,
        curry(create_chart_forced_photometry, config_state=result.config_state),
        curry(
            _group_chart_points_by_survey_band,
            error_bar=False,
            config_state=result.config_state,
        ),
        curry(_transform_to_series, series_type=FORCED_PHOTOMETRY),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.forced_photometry,
        curry(create_chart_forced_photometry, config_state=result.config_state),
        curry(
            _group_chart_points_by_survey_band,
            error_bar=True,
            config_state=result.config_state,
        ),
        curry(_transform_to_series, series_type=FORCED_PHOTOMETRY, error_bar=True),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    return result_copy


def create_chart_detections(detections: List[BaseDetection], config_state: ConfigState) -> List[ChartPoint]:
    result: list[ChartPoint] = []

    for det in detections:
        if ( det.survey_id.lower() == ZTF_SURVEY ) and det.band_name() not in config_state.bands.ztf:
            continue
        if det.survey_id.lower() == LSST_SURVEY and det.band_name() not in config_state.bands.lsst:
            continue
        if det.survey_id.lower() == ZTF_DR_SURVEY and det.band_name() not in config_state.bands.ztf_dr:
            continue

        #filtro solo det de lsst
        if det.survey_id.lower() == LSST_SURVEY and det.oid != int(config_state.oid):
            continue


        result.append(
            ChartPoint(
                det.survey_id,
                det.band_name(),
                det.phase(config_state.period) if config_state.fold else det.mjd,
                (
                    det.magnitude2flux(config_state.total, config_state.absolute)
                    if config_state.flux
                    else det.flux2magnitude(config_state.total, config_state.absolute)
                ),
                (
                    det.magnitude2flux_err(config_state.total, config_state.absolute)
                    if config_state.flux
                    else det.flux2magnitude_err(config_state.total, config_state.absolute)
                ),
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
        
        if ndet.survey_id.lower() == ZTF_DR_SURVEY and ndet.band_name() not in config_state.bands.ztf_dr:
            continue

        if ndet.survey_id.lower() == LSST_SURVEY and ndet.oid != int(config_state.oid):
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
        if fphot.survey_id.lower() == ZTF_DR_SURVEY and fphot.band_name() not in config_state.bands.ztf_dr:
            continue


        if fphot.survey_id.lower() == LSST_SURVEY and fphot.oid != int(config_state.oid):
            continue

        result.append(
            ChartPoint(
                fphot.survey_id,
                fphot.band_name(),
                fphot.phase(config_state.period) if config_state.fold else fphot.mjd,
                (
                    fphot.magnitude2flux(config_state.total)
                    if config_state.flux
                    else fphot.flux2magnitude(config_state.total)
                ),
                (
                    fphot.magnitude2flux_err(config_state.total)
                    if config_state.flux
                    else fphot.flux2magnitude_err(config_state.total)
                ),
            )
        )
    if config_state.fold:
        result.extend([ChartPoint(point.survey, point.band, point.x + 1, point.y, point.error) for point in result])

    return result

def set_chart_options_external_sources(result: Result) -> Result:
    result_copy = result.copy()

    if len(result_copy.lightcurve.detections) == 0 or not result.config_state.external_sources.enabled:
        return result_copy


    meanra = result.config_state.meanra
    meandec = result.config_state.meandec

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


def get_ztf_dr_objects(
    config_state: ConfigState,
    detections: list[BaseDetection],
    non_detections: list[BaseNonDetection],
    forced_photometry: list[BaseForcedPhotometry],
) -> Result:
    result = Result(
        {},
        Lightcurve(
            detections=detections,
            non_detections=non_detections,
            forced_photometry=forced_photometry,
        ),
        config_state=validate_config_state(config_state),
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
    )

    if len(result.lightcurve.detections) == 0:
        return result

    meanra = result.config_state.meanra
    meandec = result.config_state.meandec

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
        max_error = 99999 if config_state.flux else 1
        point_value = point.point() if not error_bar else point.error_bar(max_error)
        max_brightness, min_brightness = _get_max_and_min_brightness(config_state)
        if _valid_point(point_value, max_brightness, min_brightness):
            group[point.survey][point.band].append(point_value)

        return group

    return reduce(_add_point_to_group, chart_points, defaultdict(lambda: defaultdict(list)))

def _get_max_and_min_brightness(config_state: ConfigState):
    max_brightness = 999999 if config_state.flux else 99
    min_brightness = -999999 if config_state.flux else 0

    if config_state.survey_id == 'lsst':
        max_brightness = 9999999 if config_state.flux else 99
        min_brightness = -9999999 if config_state.flux else 0

    return max_brightness, min_brightness

def _valid_point(point: List[float], max_brightness: float, min_brightness: float) -> bool:
    valid = True

    if point[1] >= max_brightness:
        valid = False

    if point[1] <= min_brightness:
        valid = False


    return valid


def _valid_error_bar(point: List[float]) -> bool:
    return True  # just default to always valid, but can be customized later


def _transform_to_series(
    grouped_data: dict[str, dict[str, List[List[float]]]],
    series_type: str,
    error_bar=False,
) -> List[dict]:
    """Transform grouped data into series."""

    def _create_series_for_band(
        survey_band_data: tuple[str, dict[str, List[List[float]]]],
    ):
        survey, bands_data = survey_band_data

        def _process_band(band_data: tuple[str, List[List[float]]]):
            band, data = band_data



            return (
                create_series(series_type, survey, band, data)
                if not error_bar
                else create_error_bar_series(series_type, survey, band, data)
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
                detections,
                set(list(ztfDetection.model_fields.keys()) + list(LsstDetection.model_fields.keys())),
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


def offset_bands(result: Result) -> Result:
    """
    Apply vertical offsets to lightcurve bands to separate them visually.

    When band offsetting is enabled in the configuration, this function:
    1. Separates series into normal data points and error bars
    2. Calculates a metric for each series to determine offset order
    3. Applies increasing multiplicative offsets to y-values based on sort order
    4. Preserves the relationship between data points and their error bars

    Args:
        result: Result object containing echart_options with series data

    Returns:
        Result: New Result object with offset series data

    Usage example:
        # Apply band offsets to a lightcurve plot result
        result_with_offsets = offset_bands(plot_result)

        # Or use within a pipeline (as shown in lightcurve_plot function):
        result = pipe(
            get_lightcurve(...),
            set_default_echart_options,
            calculate_period,
            set_chart_options_detections,
            set_chart_options_non_detections,
            set_chart_options_forced_photometry,
            offset_bands,  # Apply band offsets as final step
        )
    """
    if not result.config_state.offset_bands:
        return result

    result_copy = result.copy()
    series_defs = result_copy.echart_options["series"]

    series, error_bars = _extract_series(series_defs, result.config_state.offset_metric)

    new_series = []
    # Flatten the structure and sort by metric
    sorted_items = []
    for survey in series:
        for band in series[survey]:
            sorted_items.append((series[survey][band]["series"], series[survey][band]["metric"]))

    # Sort by metric in ascending order
    sorted_items.sort(key=lambda x: x[1])

    for i, (sdata, _) in enumerate(sorted_items):
        for sseries in sdata:
            new_series.extend(
                _apply_offset(
                    i * result.config_state.offset_num,
                    sseries,
                    error_bars.get(sseries["name"]),
                )
            )

    result_copy.echart_options["series"] = new_series
    return result_copy


def _metric(name: str, values: List[float]) -> float:
    if name == "max":
        return max(values)
    if name == "min":
        return min(values)
    if name == "avg":
        return sum(values) / len(values)
    if name == "median":
        return calculate_median(values)

    return 99999


def calculate_median(numbers) -> float:
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)

    if n == 0:
        return 99999

    mid = n // 2

    if n % 2 == 1:
        # Odd number of elements - return middle element
        return sorted_numbers[mid]
    else:
        # Even number of elements - return average of two middle elements
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2


def _extract_series(series_defs: List[Dict[str, Any]], metric: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Split into normal series and error bars."""
    series = defaultdict(lambda: {})
    error_bars = {}
    for s in series_defs:
        if s.get("error_bar"):
            error_bars[s["name"]] = s
        else:
            if series[s["survey"]].get(s["band"]) is None:
                series[s["survey"]][s["band"]] = {
                    "series": [s],
                    "metric": _metric(metric, [d[1] for d in s["data"]]),
                }
            else:
                series[s["survey"]][s["band"]]["series"].append(s)
                series[s["survey"]][s["band"]]["metric"] = _metric(
                    metric,
                    [d[1] for x in series[s["survey"]][s["band"]]["series"] for d in x["data"]],
                )
    return series, error_bars


def _apply_offset(i: int, series: Dict[str, Any], error_bar: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    """Return a list containing the offset series and optional error bar."""

    def offset_points(points: List[List[float]]) -> List[List[float]]:
        return [[x, y + i] for x, y in points]

    def offset_errors(points: List[dict]) -> List[dict]:
        new_points = []
        for point in points:
            new_points.append(
                [
                    {
                        "coord": [point[0]["coord"][0], point[0]["coord"][1] + i],
                        "symbol": "none",
                    },
                    {
                        "coord": [point[1]["coord"][0], point[1]["coord"][1] + i],
                        "symbol": "none",
                    },
                ]
            )
        return new_points

    updated_series = {
        **series,
        "data": offset_points(series["data"]),
        "name": f"{series['name']} + {i}",
    }
    outputs = [updated_series]

    if error_bar is not None:
        updated_error = {
            **error_bar,
            "data": offset_points(error_bar["data"]),
            "markLine": {
                "data": offset_errors(error_bar["markLine"]["data"]),
                "lineStyle": error_bar["markLine"]["lineStyle"],
            },
            "name": f"{error_bar['name']} + {i}",
        }
        outputs.append(updated_error)

    return outputs
