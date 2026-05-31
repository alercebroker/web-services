"""Drift guard for the precomputed plot variants.

The lightcurve widget renders client-side (lightcurve-app.js) but does NOT convert
flux<->magnitude itself: the server precomputes every flux/total combination via
``plot_variants`` and the browser only looks the values up. These tests pin a few
known inputs to their expected plotted numbers, so any change to a conversion
formula (zero points, error propagation, sign handling) fails loudly here instead
of silently desyncing the chart from the API.

If you intentionally change a conversion in models/detections.py or
models/force_photometry.py, update the expected values below in the same commit.
"""

import pytest

from lightcurve_api.models.detections import (
    LsstDetection,
    ZtfDataReleaseDetection,
    ztfDetection,
)
from lightcurve_api.models.force_photometry import (
    LsstForcedPhotometry,
    ZtfForcedPhotometry,
)

APPROX = dict(rel=1e-9)


def _ztf_detection() -> ztfDetection:
    return ztfDetection(
        oid=1,
        survey_id="ztf",
        measurement_id=10,
        pid=0,
        diffmaglim=0,
        isdiffpos=1,
        nid=0,
        magpsf=20.0,
        sigmapsf=0.1,
        magap=0,
        sigmagap=0,
        distnr=0,
        rb=0,
        rbversion="0",
        magapbig=0,
        sigmagapbig=0,
        magpsf_corr=19.0,
        sigmapsf_corr=0.0,
        sigmapsf_corr_ext=0.2,
        corrected=True,
        dubious=False,
        has_stamp=False,
        mjd=59000.0,
        ra=10.0,
        dec=20.0,
        band=1,
    )


def _lsst_detection() -> LsstDetection:
    return LsstDetection(
        oid=1,
        survey_id="lsst",
        measurement_id=10,
        parentDiaSourceId=None,
        diaObjectId=None,
        psfFlux=100.0,
        psfFluxErr=2.0,
        psfFlux_flag=0,
        psfFlux_flag_edge=0,
        psfFlux_flag_noGoodPixels=0,
        scienceFlux=150.0,
        scienceFluxErr=3.0,
        mjd=59000.0,
        ra=10.0,
        dec=20.0,
        band=1,
        has_stamp=False,
        visit=1,
        detector=1,
        x=1.0,
        y=1.0,
        timeProcessedMjdTai=1.0,
    )


def _ztf_dr_detection() -> ZtfDataReleaseDetection:
    return ZtfDataReleaseDetection(
        band=1,
        fid=1,
        field=100,
        objectid=42.0,
        mjd=59000.0,
        mag_corr=18.5,
        e_mag_corr_ext=0.15,
        ra=10.0,
        dec=20.0,
    )


def _ztf_forced_photometry() -> ZtfForcedPhotometry:
    return ZtfForcedPhotometry(
        oid=1,
        survey_id="ztf",
        measurement_id=10,
        pid=0,
        mag=20.0,
        e_mag=0.1,
        mag_corr=19.0,
        e_mag_corr=0.2,
        e_mag_corr_ext=0.2,
        isdiffpos=1,
        corrected=True,
        dubious=False,
        field=100,
        rcid=0,
        rfid=0,
        sciinpseeing=0,
        scibckgnd=0,
        scisigpix=0,
        magzpsci=0,
        magzpsciunc=0,
        magzpscirms=0,
        clrcoeff=0,
        clrcounc=0,
        exptime=0,
        adpctdif1=0,
        adpctdif2=0,
        diffmaglim=0,
        programid=0,
        procstatus="0",
        distnr=0,
        ranr=0,
        decnr=0,
        magnr=0,
        sigmagnr=0,
        chinr=0,
        sharpnr=0,
        mjd=59000.0,
        ra=10.0,
        dec=20.0,
        band=1,
    )


def _lsst_forced_photometry() -> LsstForcedPhotometry:
    return LsstForcedPhotometry(
        oid=1,
        survey_id="lsst",
        measurement_id=10,
        mjd=59000.0,
        ra=10.0,
        dec=20.0,
        band=1,
        visit=1,
        detector=1,
        psfFlux=100.0,
        psfFluxErr=2.0,
        scienceFlux=150.0,
        scienceFluxErr=3.0,
    )


def test_variant_keys_are_the_four_toggle_combinations():
    variants = _ztf_detection().plot_variants()
    assert set(variants) == {"mag_diff", "mag_total", "flux_diff", "flux_total"}
    for v in variants.values():
        assert set(v) == {"y", "err", "sign"}


def test_ztf_detection_variants():
    v = _ztf_detection().plot_variants()

    # magnitude = raw magpsf (diff) / magpsf_corr (total); error = sigmapsf / sigmapsf_corr_ext
    assert v["mag_diff"]["y"] == pytest.approx(20.0, **APPROX)
    assert v["mag_diff"]["err"] == pytest.approx(0.1, **APPROX)
    assert v["mag_total"]["y"] == pytest.approx(19.0, **APPROX)
    assert v["mag_total"]["err"] == pytest.approx(0.2, **APPROX)

    # flux = 10 ** (-0.4 * (mag - 23.9)) * 1000 (nJy)
    assert v["flux_diff"]["y"] == pytest.approx(36307.8054770101, **APPROX)
    assert v["flux_diff"]["err"] == pytest.approx(3630.78054770101, **APPROX)
    assert v["flux_total"]["y"] == pytest.approx(91201.08393559087, **APPROX)
    assert v["flux_total"]["err"] == pytest.approx(18240.216787118174, **APPROX)

    # ZTF carries the raw isdiffpos as its sign in every variant.
    assert {variant["sign"] for variant in v.values()} == {"1"}


def test_lsst_detection_variants():
    v = _lsst_detection().plot_variants()

    # magnitude = 31.4 - 2.5 * log10(flux)
    assert v["mag_diff"]["y"] == pytest.approx(26.4, **APPROX)
    assert v["mag_diff"]["err"] == pytest.approx(0.02171472409516259, **APPROX)
    assert v["mag_total"]["y"] == pytest.approx(25.959771852360795, **APPROX)
    assert v["mag_total"]["err"] == pytest.approx(0.021714724095162587, **APPROX)

    # flux = the raw psfFlux (diff) / scienceFlux (total)
    assert v["flux_diff"]["y"] == pytest.approx(100.0, **APPROX)
    assert v["flux_diff"]["err"] == pytest.approx(2.0, **APPROX)
    assert v["flux_total"]["y"] == pytest.approx(150.0, **APPROX)
    assert v["flux_total"]["err"] == pytest.approx(3.0, **APPROX)

    assert {variant["sign"] for variant in v.values()} == {"+"}


def test_ztf_dr_detection_variants():
    # ZTF DR ignores the diff/total toggle (always corrected), so both columns match.
    v = _ztf_dr_detection().plot_variants()

    assert v["mag_diff"]["y"] == pytest.approx(18.5, **APPROX)
    assert v["mag_total"]["y"] == pytest.approx(18.5, **APPROX)
    assert v["mag_diff"]["err"] == pytest.approx(0.15, **APPROX)

    assert v["flux_diff"]["y"] == pytest.approx(144543.97707459264, **APPROX)
    assert v["flux_total"]["y"] == pytest.approx(144543.97707459264, **APPROX)
    assert v["flux_diff"]["err"] == pytest.approx(21681.596561188893, **APPROX)


def test_ztf_forced_photometry_variants():
    v = _ztf_forced_photometry().plot_variants()

    assert v["mag_diff"]["y"] == pytest.approx(20.0, **APPROX)
    assert v["mag_total"]["y"] == pytest.approx(19.0, **APPROX)
    assert v["flux_diff"]["y"] == pytest.approx(36307.8054770101, **APPROX)
    assert v["flux_total"]["y"] == pytest.approx(91201.08393559087, **APPROX)

    # Forced photometry is always plotted with a positive sign.
    assert {variant["sign"] for variant in v.values()} == {"+"}


def test_lsst_forced_photometry_variants():
    v = _lsst_forced_photometry().plot_variants()

    assert v["mag_diff"]["y"] == pytest.approx(26.4, **APPROX)
    assert v["mag_total"]["y"] == pytest.approx(25.959771852360795, **APPROX)
    assert v["flux_diff"]["y"] == pytest.approx(100.0, **APPROX)
    assert v["flux_total"]["y"] == pytest.approx(150.0, **APPROX)
    assert {variant["sign"] for variant in v.values()} == {"+"}
