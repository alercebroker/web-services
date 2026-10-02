import gzip
import io

import astropy.io.fits as fio
from matplotlib.figure import Figure
import numpy as np
from scipy import ndimage


def _read_compressed_fits(compressed_fits_file, compressed):
    fits = io.BytesIO(compressed_fits_file)
    if compressed:
        return fio.open(gzip.open(fits))[0]
    else:
        return fio.open(fits)[0]


def get_max(data, window):
    x = data.shape[0] // 2
    y = data.shape[1] // 2
    center = data[x - window : x + window, y - window : y + window]
    max_val = np.nanmax(center)
    min_val = np.nanmin(data) + 0.2 * np.nanmedian(np.abs(data - np.nanmedian(data)))

    return max_val, min_val


def transform(compressed_fits_file, file_type, window, compressed):
    hdu = _read_compressed_fits(compressed_fits_file, compressed)

    data = hdu.data
    vmax, vmin = (
        get_max(data, window)
        if file_type != "difference" or file_type != "cutoutDifference"
        else (np.nanmax(data), np.nanmin(data))
    )

    buf = io.BytesIO()

    # A Figure built directly, not through pyplot: pyplot keeps a global "current figure", so two threads
    # rendering at once could draw into each other's image. This figure belongs to this call only.
    fig = Figure()
    ax = fig.add_subplot()

    opts = dict(cmap="Greys_r", interpolation="nearest", vmin=vmin, vmax=vmax)
    try:  # Transformation required to properly orient ATLAS stamps
        data = ndimage.rotate(data, hdu.header["PA"])
        opts["origin"] = "lower"
    except KeyError:  # Required for ZTF
        opts["origin"] = "upper"
    ax.imshow(data, **opts)

    ax.axis("off")
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)

    buf.seek(0)
    return buf.read()
