"""Observation times on the BJD_TDB scale: when the light would have reached the Solar System barycentre, on
the TDB clock, at the middle of the exposure.

The raw times differ by survey, so each point is converted by its own survey:

- ZTF alerts and forced photometry: MJD in UTC at the *start* of the exposure, moved to mid-exposure with the
  exposure time. Forced photometry carries it (``exptime``, seconds); a detection takes the one of the forced
  photometry point of the same exposure (``pid``), which the light curve already has. Only where neither exists
  (about 60% of detections, from before ZTF sent forced photometry) the standard ``ZTF_DEFAULT_EXPTIME`` is
  assumed. The data-quality table also has it, but for few detections, and a cold join on it took 0.5 s.
- LSST: ``midpointMjdTai``, already mid-exposure, in TAI.
- ZTF data release: ``hmjd``, heliocentric (the Earth-orbit delay is already removed, relative to the Sun's
  centre) and mid-exposure, assumed UTC. Only the Sun's offset from the barycentre is added, so the orbit term
  isn't applied twice.

Then the Earth-orbit delay, up to about ±8.3 min, is the projection of Earth's barycentric position onto the
direction of the source, divided by the speed of light. It is computed at Earth's centre with astropy's built-in
ephemeris: leaving out the observatory's position on Earth and the Shapiro delay costs at most about 26 ms, and
needs no Earth-rotation (IERS) tables, which a pod without internet couldn't refresh.

Results are MJDs on the BJD_TDB scale. Use one sky position for all the points of a light curve (the object's
mean position): members of an association group a few arcseconds apart differ by at most about 12 ms.
"""

import warnings
from collections import defaultdict
from typing import Iterable, Sequence

import astropy.units as u
import numpy as np
from astropy.coordinates import get_body_barycentric
from astropy.time import Time
from astropy.utils import iers
from astropy.utils.exceptions import AstropyWarning
from scipy.interpolate import CubicSpline

ZTF_DEFAULT_EXPTIME = 30.0  # seconds: the standard ZTF exposure, 99% of them
SECONDS_PER_DAY = 86400.0
LIGHT_SECONDS_PER_AU = (1 * u.au).to_value(u.lightsecond)

# survey → (time scale of its raw times, True if they are already heliocentric)
_SURVEY_TIMES = {
    "ztf": ("utc", False),
    "lsst": ("tai", False),
    "ztf dr": ("utc", True),
}


def direction(ra: float, dec: float) -> np.ndarray:
    """Unit vector towards (ra, dec), in degrees, in the ICRS frame of the ephemeris."""
    ra_rad, dec_rad = np.radians(ra), np.radians(dec)
    return np.array([np.cos(dec_rad) * np.cos(ra_rad), np.cos(dec_rad) * np.sin(ra_rad), np.sin(dec_rad)])


def mean_position(ra: Sequence[float], dec: Sequence[float]) -> tuple[float, float]:
    """Mean sky position, averaging unit vectors: a plain mean of RA puts an object at RA 0, seen on both sides of
    0/360, at RA 180."""
    ra_rad, dec_rad = np.radians(np.asarray(ra, float)), np.radians(np.asarray(dec, float))
    x, y, z = (
        np.mean(np.cos(dec_rad) * np.cos(ra_rad)),
        np.mean(np.cos(dec_rad) * np.sin(ra_rad)),
        np.mean(np.sin(dec_rad)),
    )
    mean_ra = float(np.degrees(np.arctan2(y, x)) % 360)
    return (0.0 if mean_ra >= 360 else mean_ra), float(np.degrees(np.arctan2(z, np.hypot(x, y))))


def bjd_tdb(
    mjd: Sequence[float],
    survey: str,
    ra: float,
    dec: float,
    exptime: Sequence[float | None] | None = None,
) -> np.ndarray:
    """MJD on the BJD_TDB scale, at mid-exposure, of the raw times of one survey.

    ``exptime`` (seconds, ZTF only) is per point; None or NaN means unknown.
    """
    survey = survey.lower()
    if survey not in _SURVEY_TIMES:
        raise ValueError(f"No time conversion for survey {survey!r}")
    scale, heliocentric = _SURVEY_TIMES[survey]
    mjd = np.asarray(mjd, dtype=float)
    if mjd.size == 0:
        return mjd

    if survey == "ztf":
        seconds = np.full(mjd.shape, ZTF_DEFAULT_EXPTIME)
        if exptime is not None:
            given = np.array([np.nan if e is None else e for e in exptime], dtype=float)
            seconds = np.where(np.isfinite(given) & (given > 0), given, ZTF_DEFAULT_EXPTIME)
        mjd = mjd + seconds / 2 / SECONDS_PER_DAY

    # UTC/TAI → TT is exact and cheap (leap seconds and a constant). What's left, TDB − TT plus the light delay, is
    # smooth: computed on a coarse grid and interpolated when there are more points than grid nodes.
    # Leap seconds come from the table astropy ships (astropy-iers-data); once it passes its expiry date, astropy
    # would try to download a newer one in the middle of a request. A new leap second needs a package upgrade.
    with iers.conf.set_temp("auto_download", False), warnings.catch_warnings():
        warnings.simplefilter("ignore", AstropyWarning)  # "leap-second file is expired"
        tt = Time(mjd, format="mjd", scale=scale).tt.mjd
    grid = np.arange(tt.min() - GRID_STEP_DAYS, tt.max() + 2 * GRID_STEP_DAYS, GRID_STEP_DAYS)
    if len(grid) >= len(tt):
        return tt + _remainder_seconds(tt, ra, dec, heliocentric) / SECONDS_PER_DAY
    spline = CubicSpline(grid, _remainder_seconds(grid, ra, dec, heliocentric))
    return tt + spline(tt) / SECONDS_PER_DAY


GRID_STEP_DAYS = (
    5.0  # interpolation error under 0.4 ms (Earth's annual orbit and its monthly wobble); 55 ms for 8 years
)


def _remainder_seconds(tt_mjd: np.ndarray, ra: float, dec: float, heliocentric: bool) -> np.ndarray:
    """BJD_TDB − TT, in seconds, at TT times: the TDB − TT clock term plus the light delay to the barycentre."""
    t = Time(tt_mjd, format="mjd", scale="tt").tdb
    # Heliocentric times already include Earth's orbit around the Sun: only the Sun's offset from the barycentre
    # is left. Otherwise, Earth's whole offset.
    body = "sun" if heliocentric else "earth"
    position = get_body_barycentric(body, t).xyz.to_value(u.au)  # (3, n)
    delay = direction(ra, dec) @ position * LIGHT_SECONDS_PER_AU
    return (t.mjd - tt_mjd) * SECONDS_PER_DAY + delay


def ztf_exposure_times(forced_photometry: Iterable) -> dict[int, float]:
    """Exposure time (seconds) by ZTF exposure (``pid``), from forced photometry, to place detections of the same
    exposures at mid-exposure."""
    return {
        fp.pid: fp.exptime
        for fp in forced_photometry
        if fp.survey_id.lower() == "ztf" and getattr(fp, "exptime", None) is not None
    }


def bjd_tdb_of(points: Iterable, ra: float, dec: float, exptime_by_pid: dict[int, float] | None = None) -> list[float]:
    """BJD_TDB of detections or forced photometry of any survey, in their order: one batch per survey.

    Reads ``mjd``, ``survey_id`` and the exposure time of each point: its own ``exptime``, else the one of its
    ``pid`` in ``exptime_by_pid`` (see ztf_exposure_times).
    """
    points = list(points)
    exptime_by_pid = exptime_by_pid or {}

    def exposure_time(point):
        own = getattr(point, "exptime", None)
        return own if own is not None else exptime_by_pid.get(getattr(point, "pid", None))

    by_survey = defaultdict(list)
    for i, point in enumerate(points):
        by_survey[point.survey_id.lower()].append(i)

    times = [float("nan")] * len(points)
    for survey, indexes in by_survey.items():
        converted = bjd_tdb(
            [points[i].mjd for i in indexes],
            survey,
            ra,
            dec,
            [exposure_time(points[i]) for i in indexes],
        )
        for i, value in zip(indexes, converted):
            times[i] = float(value)
    return times
