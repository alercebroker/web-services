import copy
from typing import List, Sequence

import numpy as np
import pandas as pd
from toolz import curry, pipe

from core.periodogram.barycentric import bjd_tdb_times
from core.periodogram.periodogram import PeriodogramComputer
from lightcurve_api.models.lightcurve_item import BaseDetection, BaseForcedPhotometry

from ...models.periodogram import NoPeriodError, Periodogram
from ..lightcurve_plot_service.result import Result


def compute_periodogram(
    result: Result,
    member_detections: Sequence[BaseDetection] = (),
    member_forced_photometry: Sequence[BaseForcedPhotometry] = (),
) -> Result:
    """Compute periodogram for lightcurve data and update result with period information.

    This function computes a periodogram using the lightcurve detections and updates
    the result object with the computed periodogram. If the original period is set
    to the default value (0.05), it will be replaced with the best period found.

    Args:
        result: The result object containing lightcurve data and configuration
        member_detections: Detections of other objects of the viewed object's group that the user drew, of
            any survey, searched together with the object's own. Each survey's band is a band of its own
            (see band_key), so offsets between surveys don't hide the period.
        member_forced_photometry: Their forced photometry, only for the ZTF exposure times

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

    computer = PeriodogramComputer()
    detections = filter_survey_detections(result.lightcurve.detections, result.config_state.survey_id)
    detections += member_detections
    forced_photometry = [*result.lightcurve.forced_photometry, *member_forced_photometry]
    # The times the browser folds on (see core.periodogram.barycentric)
    times, _ = bjd_tdb_times(detections, forced_photometry, result.config_state.meanra, result.config_state.meandec)
    df = detections2dataframe(detections, times)
    if df.empty:
        # No corrected detections to compute it from: same empty periodogram as when no period is found
        result.periodogram = Periodogram(periods=[], scores=[], best_periods=[], best_periods_index=[])
        return result
    computed = computer.compute(df)
    result.periodogram = computed

    try:
        if result.config_state.period == 0.05:  # if period is the default, set the computed period
            result.config_state.period = computed.get_best_period()

        return result
    except NoPeriodError:
        # We set the periodogram to empty if no period is found
        # Otherwise, the arrays are filled with NaN values that occupy space
        result.periodogram.best_periods = []
        result.periodogram.best_periods_index = []
        result.periodogram.periods = []
        result.periodogram.scores = []
        return result


SURVEY_BAND_OFFSET = {"ztf": 0, "lsst": 100}

# Smallest magnitude error when the search mixes surveys. Points weigh 1/error², and LSST's errors (photon noise
# only, a few mmag) would otherwise outweigh ZTF's and pull the period off. One survey alone keeps its errors.
MIXED_SURVEYS_MIN_ERROR = 0.03


def band_key(detection: BaseDetection) -> int:
    """The band of a detection for the periodogram, one per survey and band: ZTF g and LSST g are different bands
    (and their numbers overlap: g is 1 in both). The periodogram fits each band around its own mean, so a constant
    offset between surveys, as their total magnitudes have, doesn't count against a period."""
    return SURVEY_BAND_OFFSET.get(detection.survey_id.lower(), 0) + detection.band


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


def detections2dataframe(detections: List[BaseDetection], times: Sequence[float | None] | None = None):
    """Convert a list of detections to a pandas DataFrame suitable for periodogram analysis.

    The DataFrame contains columns for MJD (Modified Julian Date), brightness (magnitude),
    brightness error, and filter ID (fid). ``times``, one per detection, replace the observed
    MJDs where given: the BJD_TDB times, as MJDs, so short periods aren't blurred by Earth's orbit.

    Total magnitude is used instead of difference, since folded lightcurve also uses corrected magnitudes.
    Detections without a corrected magnitude are left out, as they have no total magnitude to use.

    Detections without a usable magnitude are left out: an uncorrected ZTF detection has no corrected
    magnitude and comes as 0 with error 0, and a single error of 0 gets an infinite weight in the
    periodogram, turning every score into NaN.

    When the detections come from more than one survey, errors below MIXED_SURVEYS_MIN_ERROR are raised to
    it, so no survey takes over the search by its small errors alone.

    Args:
        detections: List of lightcurve detections

    Returns:
        DataFrame with columns: mjd, brightness, e_brightness, fid

    Example:
        >>> df = detections2dataframe(detections)
        >>> df.columns
        Index(['mjd', 'brightness', 'e_brightness', 'fid'], dtype='object')
    """
    times = times if times is not None else [None] * len(detections)
    rows = [
        {
            "mjd": det.mjd if time is None else time,
            "brightness": det.flux2magnitude(True, False),
            "e_brightness": det.flux2magnitude_err(True, False),
            "fid": band_key(det),
            "survey": det.survey_id.lower(),
        }
        for det, time in zip(detections, times)
        if det.has_total()
    ]
    df = pd.DataFrame(rows, columns=["mjd", "brightness", "e_brightness", "fid", "survey"])
    df = df.astype({"mjd": float, "brightness": float, "e_brightness": float, "fid": int})
    usable = (
        np.isfinite(df["brightness"])
        & (df["brightness"] != 0)
        & np.isfinite(df["e_brightness"])
        & (df["e_brightness"] > 0)
    )
    df = df[usable].reset_index(drop=True)
    if df["survey"].nunique() > 1:
        df["e_brightness"] = np.maximum(df["e_brightness"], MIXED_SURVEYS_MIN_ERROR)
    return df.drop(columns="survey")


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
        "xAxis": {"type": "log", "name": "Period", "scale": True, "splitLine": False, "min": "0.05", "max": "500"},
        "yAxis": {
            "type": "value",
            "name": "Score",
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
