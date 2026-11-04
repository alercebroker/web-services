import gzip
import io

import astropy.io.fits as fio
from matplotlib.figure import Figure
from matplotlib.transforms import Affine2D
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


def north_up_angle(header):
    """
    Degrees to rotate the stamp, counterclockwise with the FITS y axis up, so that North points up and East left.

    Rubin's mount turns the field between visits, so the same object comes out at a different angle in each alert.
    None when the stamp has no WCS (ZTF). LSST stamps carry PC + CDELT but no CTYPE, so astropy's WCS can't be used.
    """
    if "PC1_1" not in header:
        return None
    pc = np.array([[header["PC1_1"], header.get("PC1_2", 0)], [header.get("PC2_1", 0), header["PC2_2"]]])
    cd = pc * np.array([[header.get("CDELT1", 1)], [header.get("CDELT2", 1)]])
    north = np.linalg.inv(cd)[:, 1]  # pixel-space direction of increasing Dec
    return np.degrees(np.arctan2(north[0], north[1]))


def transform(compressed_fits_file, file_type, window, compressed, north_up=False):
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
    angle = north_up_angle(hdu.header) if north_up else None
    if angle is not None:
        # Rotate the drawing, not the data: pixels stay crisp, and turning about the reference pixel (the alert)
        # inside fixed limits keeps the image size and leaves the alert under the crosshair
        cx, cy = hdu.header["CRPIX1"] - 1, hdu.header["CRPIX2"] - 1
        ny, nx = data.shape
        ax.imshow(data, origin="lower", transform=Affine2D().rotate_deg_around(cx, cy, angle) + ax.transData, **opts)
        ax.set_xlim(cx - nx / 2, cx + nx / 2)
        ax.set_ylim(cy - ny / 2, cy + ny / 2)
    else:
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
