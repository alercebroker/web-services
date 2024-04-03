import logging
from .shared import base_options, get_bands, hex2rgb
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

band_map = {
    1: {"name": "g", "color": "#56E03A"},
    2: {"name": "r", "color": "#D42F4B"},
    101: {"name": "g DR5", "color": "#ADA3A3"},
    102: {"name": "r DR5", "color": "#377EB8"},
    103: {"name": "i DR5", "color": "#FF7F00"},
    4: {"name": "c", "color": "#00FFFF"},
    5: {"name": "o", "color": "#FFA500"},
}


def apparent_lightcurve_options(
    detections, forced_photometry, plot_text_color, ralidator
) -> dict:
    """Apparent lightcurve options for echarts.

    Parameters
    ----------
    detections : list
        List of detections.
    non_detections : list
        List of non detections.
    forced_photometry : list
        List of forced photometry.
    plot_text_color : str
        Plot text color.
    ralidator : Ralidator
        Ralidator instance from the request.

    Returns
    -------
    dict
        Difference lightcurve options for echarts.
    """
    options = base_options(plot_text_color)
    set_series(options, detections, forced_photometry)
    return options


def set_series(
    options: dict,
    detections: list,
    forced_photometry: list,
):
    """Set echarts series.

    Parameters
    ----------
    options : dict
        Echarts options.
    detections : list
        List of detections.
    non_detections : list
        List of non detections.
    forced_photometry : list
        List of forced photometry.
    """
    bands = get_bands(detections)
    detection_series = get_detections_series(detections, bands)
    detection_error_bars_series = get_error_bars_series(detections, bands)
    forced_photometry_series = get_forced_photometry_series(
        forced_photometry, bands
    )
    forced_photometry_error_bars_series = get_error_bars_series(
        forced_photometry, bands, forced=True
    )
    all_series = (
        detection_series
        + detection_error_bars_series
        + forced_photometry_series
        + forced_photometry_error_bars_series
    )
    options["series"] = all_series


def get_detections_series(detections, bands):
    def _filter(band):
        def filter_detection(det):
            if (
                not det["corrected"]
                or det["mag_corr"] is None
                or det["mag_corr"] > 24
                or det["e_mag_corr_ext"] >= 1
            ):
                return False
            return det["fid"] == band

        return filter_detection

    def get_band_data(band, detections):
        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag_corr"],
                    x["candid"] if "candid" in x else x["objectid"],
                    x["e_mag_corr_ext"],
                    x["isdiffpos"] if "isdiffpos" in x else x["field"],
                ],
                filter(_filter(band), detections),
            )
        )

    def get_serie(band: int) -> dict:
        return {
            "name": band_map[band]["name"],
            "type": "scatter",
            "scale": True,
            "color": hex2rgb(band_map[band]["color"]),
            "symbolSize": 6 if band < 100 else 3,
            "symbol": "circle" if band < 100 else "square",
            "encode": {"x": 0, "y": 1},
            "zlevel": 10 if band < 100 else 0,
            "data": get_band_data(band, detections),
        }

    return list(map(lambda band: get_serie(band), bands))


def get_error_bars_series(detections, bands, forced=False):
    def get_band_data(band, forced):
        def _filter(det):
            if forced:
                if "distnr" in det["extra_fields"]:
                    return (
                        det["extra_fields"]["distnr"] >= 0
                        and det["fid"] == band
                        and det["corrected"]
                        and det["mag_corr"] is not None
                        and det["mag_corr"] <= 24
                        and det["e_mag_corr_ext"] < 1
                    )
                else:
                    return False
            return (
                det["fid"] == band
                and det["corrected"]
                and det["mag_corr"] is not None
                and det["mag_corr"] <= 24
                and det["e_mag_corr_ext"] < 1
            )

        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag_corr"] - x["e_mag_corr_ext"],
                    x["mag_corr"] + x["e_mag_corr_ext"],
                ],
                filter(_filter, detections),
            )
        )

    def get_serie(band: int) -> dict:
        return {
            "error_bars": True,
            "name": band_map[band]["name"] + " forced photometry"
            if forced
            else band_map[band]["name"],
            "type": "custom",
            "scale": True,
            "color": hex2rgb(band_map[band]["color"]),
            "data": get_band_data(band, forced),
        }

    return list(map(lambda band: get_serie(band), bands))


def get_forced_photometry_series(forced_photometry, bands):
    def filter_distnr(band):
        def _filter(forced_photometry):
            if (
                not forced_photometry["corrected"]
                or forced_photometry["mag_corr"] > 24
                or forced_photometry["e_mag_corr_ext"] >= 1
            ):
                return False
            if "distnr" in forced_photometry["extra_fields"]:
                return (
                    forced_photometry["extra_fields"]["distnr"] >= 0
                    and forced_photometry["fid"] == band
                )
            return forced_photometry["fid"] == band

        return _filter

    def get_band_data(band: int, forced_photometry: List[dict]):
        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag_corr"],
                    "no-candid",
                    x["e_mag_corr_ext"],
                    x["isdiffpos"],
                ],
                filter(filter_distnr(band), forced_photometry),
            )
        )

    def get_serie(band: int):
        return {
            "name": band_map[band]["name"] + " forced photometry",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": hex2rgb(band_map[band]["color"]),
            "symbol": "path://M0,0 L0,10 L10,10 L10,0 Z",
            "encode": {"x": 0, "y": 1},
            "data": get_band_data(band, forced_photometry),
        }

    return list(map(lambda band: get_serie(band), bands))
