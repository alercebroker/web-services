import copy
import csv
import io
import zipfile
from collections import defaultdict
from itertools import chain
from typing import Callable, ContextManager, List, Dict, Any, Tuple

import httpx
from lightcurve_api.models.periodogram import Periodogram
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
COLORS = {
    ZTF_SURVEY: {"g": "#56E03A", "r": "#D42F4B", "i": "#F4D617"},
    LSST_SURVEY: {"u": "#1600EA", "g": "#31DE1F", "r": "#B52626", "i": "#370201", "z": "#BA52FF", "y": "#61A2B3"},
    ZTF_DR_SURVEY: {"g": "#ADA3A3", "r": "#377EB8", "i": "#FF7F00"},
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
}


def create_series(name: str, survey: str, band: str, data: List[List[float]]) -> dict:
    return {
        "name": name + " " + survey.upper() + ": " + band,
        "type": "scatter",
        "data": data,
        "color": COLORS[survey][band],
        "symbol": SYMBOLS[survey][name]["symbol"],
    }


def create_error_bar_series(name: str, survey: str, band: str, data: List[List[float]]):
    return {
        "name": name + " " + survey.upper() + ": " + band,
        "type": "custom",
        "data": data,
        "color": COLORS[survey][band],
        "renderItem": "renderError",
        "scale": True,
    }


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
        ],
    }
    if config_state.offset_bands:
        # When offset bands are enabled, the legend is inherited from the series data
        legend["data"] = None

    return legend


def default_echarts_options(config_state: ConfigState):
    return {
        "tooltip": {},
        "grid": {"left": "left", "top": "10%", "width": "75%", "height": "100%"},
        "legend": default_echarts_legend(config_state),
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
    result = Result(
        {},
        Lightcurve(detections=[], non_detections=[], forced_photometry=[]),
        config_state=ConfigState(),
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
    )
    return pipe(
        get_lightcurve(result, oid, survey_id, session_factory),
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
            Lightcurve(detections=detections, non_detections=non_detections, forced_photometry=forced_photometry),
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
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
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
        curry(_transform_to_series, series_type=DETECTION),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.detections,
        curry(create_chart_detections, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=True, config_state=result.config_state),
        curry(_transform_to_series, series_type=DETECTION, error_bar=True),
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
        curry(_transform_to_series, series_type=NON_DETECTION),
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
        curry(_transform_to_series, series_type=FORCED_PHOTOMETRY),
        lambda series: result_copy.echart_options["series"].extend(series),
    )

    # Error bars
    pipe(
        result_copy.lightcurve.forced_photometry,
        curry(create_chart_forced_photometry, config_state=result.config_state),
        curry(_group_chart_points_by_survey_band, error_bar=True, config_state=result.config_state),
        curry(_transform_to_series, series_type=FORCED_PHOTOMETRY, error_bar=True),
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
        periodogram=Periodogram(periods=[], scores=[], best_periods_index=[], best_periods=[]),
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
        if _valid_point(point_value):
            group[point.survey][point.band].append(point_value)
        return group

    return reduce(_add_point_to_group, chart_points, defaultdict(lambda: defaultdict(list)))


def _valid_point(point: List[float]) -> bool:
    valid = True
    if point[1] <= 0:
        valid = False

    if point[1] >= 999999:
        valid = False

    return valid


def _transform_to_series(
    grouped_data: dict[str, dict[str, List[List[float]]]], series_type: str, error_bar=False
) -> List[dict]:
    """Transform grouped data into series."""

    def _create_series_for_band(survey_band_data: tuple[str, dict[str, List[List[float]]]]):
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

    # Sort and transform in a functional pipeline
    new_series = [
        output
        for i, (sname, sdata) in enumerate(sorted(series.items(), key=lambda kv: kv[1]["metric"]))
        for output in _apply_offset(i * result.config_state.offset_num, sdata, error_bars.get(sname))
    ]

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
    series = {}
    error_bars = {}
    for s in series_defs:
        if s["type"] == "custom":
            error_bars[s["name"]] = s
        else:
            series[s["name"]] = {
                "series": s,
                "metric": _metric(metric, [d[1] for d in s["data"]]),
            }
    return series, error_bars


def _apply_offset(i: int, series: Dict[str, Any], error_bar: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    """Return a list containing the offset series and optional error bar."""

    def offset_points(points: List[List[float]]) -> List[List[float]]:
        return [[x, y + i] for x, y in points]

    def offset_errors(points: List[List[float]]) -> List[List[float]]:
        # point is composed by x, y1, y2
        # where x is the x-axis value (mjd), y1 is the y-axis value plus error, and y2 is the y-axis value minus error
        return [[x, y1 + i, y2 + i] for x, y1, y2 in points]

    updated_series = {
        **series["series"],
        "data": offset_points(series["series"]["data"]),
        "name": f"{series['series']['name']} + {i}",
    }
    outputs = [updated_series]

    if error_bar is not None:
        updated_error = {**error_bar, "data": offset_errors(error_bar["data"]), "name": f"{error_bar['name']} + {i}"}
        outputs.append(updated_error)

    return outputs
