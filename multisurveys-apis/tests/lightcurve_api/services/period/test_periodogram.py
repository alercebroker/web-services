import numpy as np
import pandas as pd
import pytest

from core.periodogram.periodogram import PeriodogramComputer
from lightcurve_api.services.period.service import detections2dataframe

N_BANDS = 6
OBS_PER_BAND = 100
TIMESPAN_DAYS = 1500
NOISE_MAG = 0.01


def _synthetic_lightcurve(seed: int) -> tuple[pd.DataFrame, float]:
    """A sine light curve in 6 bands, 100 observations each, at random dates and in random order.

    Each band has its own mean magnitude, amplitude and phase. The dates span more than the
    1000 days the periodogram keeps, so the trimming runs too.
    """
    rng = np.random.default_rng(seed)
    period = float(np.exp(rng.uniform(np.log(0.1), np.log(20.0))))

    bands = []
    for fid in range(1, N_BANDS + 1):
        mjd = 58000 + rng.uniform(0, TIMESPAN_DAYS, OBS_PER_BAND)
        mean, amplitude, phase = rng.uniform(15, 18), rng.uniform(0.2, 0.5), rng.uniform(0, 2 * np.pi)
        brightness = mean + amplitude * np.sin(2 * np.pi * mjd / period + phase)
        bands.append(
            pd.DataFrame(
                {
                    "mjd": mjd,
                    "brightness": brightness + rng.normal(0, NOISE_MAG, OBS_PER_BAND),
                    "e_brightness": np.full(OBS_PER_BAND, NOISE_MAG),
                    "fid": fid,
                }
            )
        )

    lightcurve = pd.concat(bands).sample(frac=1, random_state=seed).reset_index(drop=True)
    return lightcurve, period


class _FakeDetection:
    """Just what detections2dataframe reads from a detection."""

    def __init__(self, mjd, band, magnitude, error):
        self.mjd, self.band, self._magnitude, self._error = mjd, band, magnitude, error

    def flux2magnitude(self, total, absolute):
        return self._magnitude

    def flux2magnitude_err(self, total, absolute):
        return self._error


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_periodogram_peak_is_the_true_period(seed):
    lightcurve, period = _synthetic_lightcurve(seed)

    periodogram = PeriodogramComputer().compute(lightcurve)

    assert periodogram.get_best_period() == pytest.approx(period, rel=1e-3)


def test_detection_order_does_not_change_the_periodogram():
    # Trimming to 1000 days walks the dates in order: on unsorted dates it kept all 1500 days,
    # making the frequency grid half as large again.
    lightcurve, _ = _synthetic_lightcurve(0)

    unsorted = PeriodogramComputer().compute(lightcurve)
    newest_first = PeriodogramComputer().compute(lightcurve.sort_values("mjd", ascending=False))
    oldest_first = PeriodogramComputer().compute(lightcurve.sort_values("mjd"))

    assert len(unsorted.periods) == len(newest_first.periods) == len(oldest_first.periods)
    assert unsorted.get_best_period() == newest_first.get_best_period() == oldest_first.get_best_period()


def test_detection_with_zero_error_is_left_out():
    lightcurve, period = _synthetic_lightcurve(1)
    detections = [
        _FakeDetection(row.mjd, int(row.fid), row.brightness, row.e_brightness) for row in lightcurve.itertuples()
    ]
    # An uncorrected ZTF detection: no corrected magnitude, so 0 with error 0.
    detections.append(_FakeDetection(58700.0, 2, 0.0, 0.0))
    detections.append(_FakeDetection(58701.0, 1, float("nan"), 0.01))

    df = detections2dataframe(detections)

    assert len(df) == len(lightcurve)
    assert PeriodogramComputer().compute(df).get_best_period() == pytest.approx(period, rel=1e-3)
