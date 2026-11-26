"""Observation times on the BJD_TDB scale (core.periodogram.barycentric), against astropy's full computation."""

from types import SimpleNamespace

import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.time import Time

from core.periodogram.barycentric import (
    ZTF_DEFAULT_EXPTIME,
    bjd_tdb,
    bjd_tdb_of,
    mean_position,
    ztf_exposure_times,
)

GEOCENTRE = EarthLocation.from_geocentric(0, 0, 0, u.m)
SECOND = 1 / 86400
# Mid-exposure instants (UTC MJD) over 8 years: more points than grid nodes, so the interpolated path runs
MID = np.sort(np.random.default_rng(0).uniform(58300, 61200, 1000))
POSITIONS = [(0.0, 0.0), (90.0, 23.4), (200.0, -60.0), (300.0, 60.0)]


def reference(mid_utc, ra, dec, kind="barycentric"):
    """astropy's BJD_TDB (or HJD, in UTC) at Earth's centre."""
    t = Time(mid_utc, format="mjd", scale="utc", location=GEOCENTRE)
    delay = t.light_travel_time(SkyCoord(ra * u.deg, dec * u.deg), kind)
    return (t.tdb + delay).mjd if kind == "barycentric" else (t + delay).utc.mjd


@pytest.mark.parametrize("ra, dec", POSITIONS)
def test_each_survey_matches_astropy(ra, dec):
    expected = reference(MID, ra, dec)
    ztf = bjd_tdb(MID - 15 * SECOND, "ztf", ra, dec)  # start of a 30 s exposure, exptime unknown
    lsst = bjd_tdb(Time(MID, format="mjd", scale="utc").tai.mjd, "lsst", ra, dec)  # TAI, mid-exposure

    for converted in (ztf, lsst):
        assert np.abs(converted - expected).max() < 1e-3 * SECOND


def test_ztf_uses_each_exposure_time():
    expected = reference(MID[:3], 10.0, 10.0)
    exptimes = [240.0, None, float("nan")]  # None and NaN: unknown, the standard 30 s
    starts = MID[:3] - np.array([120.0, 15.0, 15.0]) * SECOND

    converted = bjd_tdb(starts, "ztf", 10.0, 10.0, exptimes)

    assert np.abs(converted - expected).max() < 1e-3 * SECOND


def test_ztf_and_lsst_agree_on_the_same_instant():
    # The raw times of one instant differ by 52 s (UTC vs TAI, start vs middle of the exposure)
    instant = MID[:10]
    ztf = bjd_tdb(instant - ZTF_DEFAULT_EXPTIME / 2 * SECOND, "ztf", 45.0, -30.0)
    lsst = bjd_tdb(Time(instant, format="mjd", scale="utc").tai.mjd, "lsst", 45.0, -30.0)

    assert np.abs(ztf - lsst).max() < 1e-3 * SECOND


@pytest.mark.parametrize("ra, dec", POSITIONS)
def test_data_release_times_are_not_corrected_twice(ra, dec):
    # hmjd is already heliocentric: only the Sun's offset from the barycentre (and TDB) are left, a few seconds,
    # not Earth's whole orbit again (up to about 1000 s off)
    hmjd = reference(MID, ra, dec, "heliocentric")

    converted = bjd_tdb(hmjd, "ztf dr", ra, dec)

    assert np.abs(converted - reference(MID, ra, dec)).max() < 0.1e-3 * SECOND


def test_unknown_survey_is_refused():
    with pytest.raises(ValueError):
        bjd_tdb([60000.0], "atlas", 0.0, 0.0)


def test_mean_position_across_ra_zero():
    ra, dec = mean_position([359.9999, 0.0001], [10.0, 10.0])

    assert ra == pytest.approx(0.0, abs=1e-6)
    assert dec == pytest.approx(10.0)


def test_points_of_several_surveys_keep_their_order():
    points = [
        SimpleNamespace(survey_id="lsst", mjd=60100.0),
        SimpleNamespace(survey_id="ztf", mjd=60100.0, pid=7),  # a detection: its exposure time comes by pid
        SimpleNamespace(survey_id="ztf", mjd=60100.0, exptime=30.0),
    ]
    exptimes = ztf_exposure_times([SimpleNamespace(survey_id="ztf", pid=7, exptime=240.0)])

    lsst, ztf_by_pid, ztf_own = bjd_tdb_of(points, 10.0, 10.0, exptimes)

    assert ztf_by_pid == pytest.approx(bjd_tdb([60100.0], "ztf", 10.0, 10.0, [240.0])[0], abs=1e-9)
    assert ztf_own == pytest.approx(bjd_tdb([60100.0], "ztf", 10.0, 10.0)[0], abs=1e-9)
    # (240 − 30) / 2 s later, plus up to 0.01 s more light delay: Earth moves about 3000 km in that time
    assert (ztf_by_pid - ztf_own) * 86400 == pytest.approx(105.0, abs=0.02)
    assert lsst == pytest.approx(bjd_tdb([60100.0], "lsst", 10.0, 10.0)[0], abs=1e-9)
