import copy
from typing import List

import pandas as pd
from toolz import curry, pipe

from core.periodogram.periodogram import PeriodogramComputer
from lightcurve_api.models.lightcurve_item import BaseDetection

from ...models.periodogram import NoPeriodError, Periodogram
from ..lightcurve_plot_service.result import Result


def compute_periodogram(result: Result) -> Result:
    """Compute periodogram for lightcurve data and update result with period information.

    This function computes a periodogram using the lightcurve detections and updates
    the result object with the computed periodogram. If the original period is set
    to the default value (0.05), it will be replaced with the best period found.

    Args:
        result: The result object containing lightcurve data and configuration

    Returns:
        A new result object with periodogram data added

    Example:
        >>> result = Result(lightcurve=lightcurve_data, config_state=config)
        >>> result_with_periodogram = compute_periodogram(result)
        >>> print(result_with_periodogram.periodogram.get_best_period())
        1.2345
    """
    if not result.config_state.fold:
        return result

    result_copy = result.copy()

    computer = PeriodogramComputer()
    df = detections2dataframe(filter_survey_detections(result.lightcurve.detections, result.config_state.survey_id))
    computed = computer.compute(df)
    result_copy.periodogram = computed

    try:
        if result.config_state.period == 0.05:  # if period is the default, set the computed period
            result_copy.config_state.period = computed.get_best_period()

        return result_copy
    except NoPeriodError:
        # We set the periodogram to empty if no period is found
        # Otherwise, the arrays are filled with NaN values that occupy space
        result_copy.periodogram.best_periods = []
        result_copy.periodogram.best_periods_index = []
        result_copy.periodogram.periods = []
        result_copy.periodogram.scores = []
        return result_copy


def filter_survey_detections(detections: List[BaseDetection], survey_id: str) -> List[BaseDetection]:
    """Filter detections to include only those from a specific survey.

    Args:
        detections: List of lightcurve detections
        survey_id: The survey identifier to filter by (case-insensitive)

    Returns:
        Filtered list of detections from the specified survey

    Example:
        >>> detections = [det1, det2, det3]  # where det1.survey_id = 'ztf', det2.survey_id = 'atlas'
        >>> filtered = filter_survey_detections(detections, 'ztf')
        >>> len(filtered)
        1
    """
    return [d for d in detections if d.survey_id.lower() == survey_id.lower()]


def detections2dataframe(detections: List[BaseDetection]):
    """Convert a list of detections to a pandas DataFrame suitable for periodogram analysis.

    The DataFrame contains columns for MJD (Modified Julian Date), brightness (magnitude),
    brightness error, and filter ID (fid).

    Total magnitude is used instead of difference, since folded lightcurve also uses corrected magnitudes.

    Args:
        detections: List of lightcurve detections

    Returns:
        DataFrame with columns: mjd, brightness, e_brightness, fid

    Example:
        >>> df = detections2dataframe(detections)
        >>> df.columns
        Index(['mjd', 'brightness', 'e_brightness', 'fid'], dtype='object')
    """
    df_dict = {"mjd": [], "brightness": [], "e_brightness": [], "fid": []}
    for det in detections:
        df_dict["mjd"].append(det.mjd)
        df_dict["brightness"].append(det.flux2magnitude(True, False))
        df_dict["e_brightness"].append(det.flux2magnitude_err(True, False))
        df_dict["fid"].append(det.band)
    return pd.DataFrame(df_dict)


def default_echart_options():
    """Generate default ECharts configuration options for periodogram visualization.

    Returns a dictionary with pre-configured options for displaying periodogram
    data including tooltip, grid layout, legend, and axis configurations.

    Returns:
        Dictionary with ECharts configuration options

    Example:
        >>> options = default_echart_options()
        >>> 'xAxis' in options
        True
    """
    return {
        "tooltip": {
            "axisPointer": {
                "type": "cross",
            },
        },
        "grid": {"left": "left", "top": "10%", "width": "75%", "height": "100%"},
        "legend": {
            "left": "right",
            "top": "middle",
            "height": "80%",
            "orient": "vertical",
        },
        "xAxis": {"type": "value", "name": "period", "scale": True, "splitLine": False},
        "yAxis": {
            "type": "value",
            "name": "score",
            "scale": True,
            "splitLine": False,
        },
        "series": [],
        "animation": False,
    }


def get_periodogram_chart(periodogram: Periodogram) -> dict:
    """Generate ECharts configuration for visualizing a periodogram.

    Creates a complete ECharts configuration by combining default options
    with periodogram data series for both regular periods and best periods.

    Args:
        periodogram: The periodogram data to visualize

    Returns:
        Complete ECharts configuration dictionary
    """
    return pipe(
        default_echart_options(),
        curry(add_periods_series, periodogram=periodogram),
        curry(add_best_periods_series, periodogram=periodogram),
    )


def add_periods_series(options: dict, periodogram: Periodogram) -> dict:
    """Add regular period data series to ECharts options.

    Creates a scatter series for all periods in the periodogram, excluding
    the best periods which are handled separately.

    Args:
        options: Existing ECharts configuration options
        periodogram: Periodogram data containing periods and scores

    Returns:
        Updated ECharts options with periods series added

    Note: Best periods are excluded from this series and handled separately.
    """
    new_options = copy.deepcopy(options)
    new_options["series"].append({"name": "periods", "type": "scatter", "data": []})
    for i, period in enumerate(periodogram.periods):
        if i in periodogram.best_periods_index:
            continue
        new_options["series"][-1]["data"].append([period, periodogram.scores[i]])

    return new_options


def add_best_periods_series(options: dict, periodogram: Periodogram) -> dict:
    """Add best period data series to ECharts options.

    Creates a special scatter series highlighting the best periods found
    in the periodogram analysis, using triangle symbols and red color.

    Args:
        options: Existing ECharts configuration options
        periodogram: Periodogram data containing best periods information

    Returns:
        Updated ECharts options with best periods series added
    """
    new_options = copy.deepcopy(options)
    new_options["series"].append(
        {
            "name": "best periods",
            "type": "scatter",
            "data": [],
            "symbol": "triangle",
            "color": "red",
        }
    )
    for bpi in periodogram.best_periods_index:
        new_options["series"][-1]["data"].append([periodogram.periods[bpi], periodogram.scores[bpi]])

    return new_options
