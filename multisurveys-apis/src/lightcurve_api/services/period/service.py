from typing import List

import pandas as pd

from core.periodogram.periodogram import PeriodogramComputer
from lightcurve_api.models.lightcurve_item import BaseDetection

from ..lightcurve_plot_service.result import Result


def compute_periodogram(result: Result) -> Result:
    if not result.config_state.fold:
        return result

    if result.config_state.period > 0.05:  # if other than the default value use that
        return result

    result_copy = result.copy()

    computer = PeriodogramComputer()
    df = detections2dataframe(filter_survey_detections(result.lightcurve.detections, result.config_state.survey_id))
    computed = computer.compute(df)
    result_copy.period = computed

    if len(computed["best_periods_index"]) == 0:
        return result_copy

    result_copy.config_state.period = round(computed["period"][computed["best_periods_index"][0]], 3)
    return result_copy


def filter_survey_detections(detections: List[BaseDetection], survey_id: str) -> List[BaseDetection]:
    return [d for d in detections if d.survey_id.lower() == survey_id.lower()]


def detections2dataframe(detections: List[BaseDetection]):
    df_dict = {"mjd": [], "brightness": [], "e_brightness": [], "fid": []}
    for det in detections:
        df_dict["mjd"].append(det.mjd)
        df_dict["brightness"].append(det.flux2magnitude(True))
        df_dict["e_brightness"].append(det.flux2magnitude_err(True))
        df_dict["fid"].append(det.band)
    return pd.DataFrame(df_dict)
