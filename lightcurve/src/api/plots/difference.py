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

def base_options(text_color):
    grid = {
        "left": "7%",
        "right": "5%",
        "bottom": "20%",
    }
    tooltip = {
        "show": True,
        "trigger": "axis",
        "axisPointer": {"type": "cross", "label": {"backgroundColor": "#505765"}},
        # add formatter in js
    }
    toolbox = {
        "show": True,
        "showTitle": True,
        "feature": {
            "dataZoom": {
                "show": True,
                "title": {"zoom": "Zoom", "back": "Back"},
                "icon": {
                    "zoom": "M11,4A7,7 0 0,1 18,11C18,12.5 17.5,14 16.61,15.19L17.42,16H18L23,21L21,23L16,18V17.41L15.19,16.6C12.1,18.92 7.71,18.29 5.39,15.2C3.07,12.11 3.7,7.72 6.79,5.4C8,4.5 9.5,4 11,4M10,7V10H7V12H10V15H12V12H15V10H12V7H10M1,1V8L8,1H1Z",
                    "back": "M21,11H6.83L10.41,7.41L9,6L3,12L9,18L10.41,16.58L6.83,13H21V11Z",
                },
            },
            "restore": {"show": True, "title": "Restore"},
        },
        "tooltip": {
            "bacgroundColor": "#222",
            "textStyle": {"fontSize": 12},
            "extraCssText": "box-shadow: 0 0 3px rgba(0, 0, 0, 0.3);",
        }
    }
    legend = {
        "data": [],
        "bottom": 0,
        "textStyle": {"color": text_color, "fontWeight": "lighter"},
    }
    x_axis = {
        "name": "Modified Julian Date",
        "nameLocation": "center",
        "scale": True,
        "type": "value",
        "splitLine": {"show": False},
        "nameTextStyle": {"padding": 7}
    }
    y_axis = {
        "name": "Magnitude",
        "nameLocation": "start",
        "type": "value",
        "scale": True,
        "splitLine": {"show": False},
        "inverse": True,
        ## add min and max in js
    }
    return {
        "grid": grid,
        "tooltip": tooltip,
        "toolbox": toolbox,
        "legend": legend,
        "xAxis": x_axis,
        "yAxis": y_axis,
    
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
    options = base_options(plot_text_color)
    options["series"] = all_series
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

    def get_band_data(band, forced):
        def _filter(det):
            if forced and "distnr" in det["extra_fields"]:
                return det["extra_fields"]["distnr"] >= 0 and det["fid"] == band
            return det["fid"] == band

        return list(
            map(
                lambda x: [
                    x["mjd"],
                    x["mag"] - x["e_mag"],
                    x["mag"] + x["e_mag"],
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
                filter(lambda x: x["fid"] == band and x["diffmaglim"] <= 23 and x["diffmaglim"] > 10, non_detections),
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
