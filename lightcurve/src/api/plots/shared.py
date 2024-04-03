from typing import List

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
