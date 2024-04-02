from typing import List
import logging

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


def difference_lightcurve_options(
    detections, non_detections, forced_photometry, plot_text_color, ralidator
) -> dict:
    """Difference lightcurve options for echarts.

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
    bands = get_bands(detections)
    detection_series = get_detections_series(detections, bands)
    detection_error_bars_series = get_error_bars_series(detections, bands)
    non_detection_series = get_non_detections_series(non_detections, bands)
    forced_photometry_series = get_forced_photometry_series(
        forced_photometry, bands
    )
    forced_photometry_error_bars_series = get_error_bars_series(
        forced_photometry, bands, forced=True
    )
    all_series = (
        detection_series
        + detection_error_bars_series
        + non_detection_series
        + forced_photometry_series
        + forced_photometry_error_bars_series
    )
    options = {"series": all_series}
    return options


def get_detections_series(detections: List[dict], bands: list) -> List[dict]:
    """Get detections echarts series.

    Parameters
    ----------
    detections : list
        List of detections.
    bands : list
        List of bands identifiers.

    Returns
    -------
    list
        Detections echarts series.
    """

    def get_band_data(band, detections):
        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag"],
                    x["candid"],
                    x["e_mag"],
                    x["isdiffpos"],
                ],
                filter(lambda x: x["fid"] == band, detections),
            )
        )

    def get_serie(band: int) -> dict:
        return {
            "name": band_map[band]["name"],
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": hex2rgb(band_map[band]["color"]),
            "encode": {"x": 0, "y": 1},
            "data": get_band_data(band, detections),
        }

    return list(map(lambda band: get_serie(band), bands))


def get_error_bars_series(
    detections: List[dict], bands: list, forced=False
) -> List[dict]:
    """Get detections error bars echarts series.

    Parameters
    ----------
    detections : list
        List of detections or forced_photometry treated as detections.
    bands : list
        List of bands identifiers.

    Returns
    -------
    list
        Detections error bars echarts series.
    """

    def get_band_data(band):
        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag"] - x["e_mag"],
                    x["mag"] + x["e_mag"],
                ],
                filter(lambda x: x["fid"] == band, detections),
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
            "data": get_band_data(band),
        }

    return list(map(lambda band: get_serie(band), bands))


def get_non_detections_series(
    non_detections: List[dict], bands: List[int]
) -> List[dict]:
    """Get non detections echarts series.

    Parameters
    ----------
    non_detections : list
        List of non detections.
    bands : list
        List of bands identifiers.

    Returns
    -------
    list
        Non detections echarts series.
    """

    def get_band_data(band: int, non_detections: List[dict]):
        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["diffmaglim"],
                ],
                filter(lambda x: x["fid"] == band, non_detections),
            )
        )

    def get_serie(band: int):
        return {
            "name": band_map[band]["name"] + " non-detections",
            "type": "scatter",
            "symbolSize": 6,
            "scale": True,
            "color": hex2rgb(band_map[band]["color"], 0.5),
            "symbol": "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z",
            "data": get_band_data(band, non_detections),
        }

    return list(map(lambda band: get_serie(band), bands))


def get_forced_photometry_series(
    forced_photometry: List[dict], bands: List[int]
) -> List[dict]:
    """Get forced photometry echarts series.

    Parameters
    ----------
    forced_photometry : list
        List of forced photometry.
    bands : list
        List of bands identifiers.

    Returns
    -------
    list
        Forced photometry echarts series.
    """

    def filter_distnr(band):
        def _filter(forced_photometry):
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
                    x["mag"],
                    "no-candid",
                    x["e_mag"],
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


def get_bands(items: List[dict]) -> list:
    """Get bands from item.

    Parameters
    ----------
    item : list
        List of items.
        Each item has a fid field.

    Returns
    -------
    list
        Bands.

    Raises
    ------
    KeyError
        If the `fid` field is not present in the items.
    """
    try:
        return list(set(map(lambda x: x["fid"], items)))
    except KeyError:
        raise KeyError(
            "Error getting bands from items. `fid` field should be present in the items"
        )


def hex2rgb(hex: str, alpha: int = None) -> str:
    """Parses hexadecimal color to rgba.

    Parameters
    ----------
    hex : str
    alpha : i

    Returns
    -------
    str
        the rgba representation
    """
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    if alpha:
        if alpha < 0:
            alpha = 0
        elif alpha > 1:
            alpha = 1
        return f"rgba({r}, {g}, {b}, {alpha})"
    return f"rgb({r}, {g}, {b})"
