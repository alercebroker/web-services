import numpy as np
import pandas as pd
from P4J import MultiBandPeriodogram


class PeriodogramComputer:
    def __init__(self):
        self.periodogram_computer = MultiBandPeriodogram(method="MHAOV")
        self.smallest_period = 0.05
        self.largest_period = 500.0
        self.shift = 0.1
        self.trim_lightcurve_to_n_days = 1000

    def trim_lightcurve(self, lightcurve: pd.DataFrame):
        if self.trim_lightcurve_to_n_days is None or len(lightcurve) == 0:
            return lightcurve

        times = lightcurve["mjd"].values

        # indexes of the best subsequence so far
        best_starting = 0
        best_ending = 0  # index of the last obs (included)

        # subsequence being examined
        # invariant: subsequence timespan under max allowed
        starting = 0
        ending = 0  # included

        while True:
            # subsequence len
            current_n = ending - starting + 1

            # best subsequence len
            len_best_subsequence = best_ending - best_starting + 1

            if current_n > len_best_subsequence:
                best_starting = starting
                best_ending = ending

            current_timespan = times[ending] - times[starting]
            if current_timespan < self.trim_lightcurve_to_n_days:
                # try to extend the subsequence
                ending += 1

                # nothing else to do
                if ending >= len(times):
                    break

                # restore invariant
                current_timespan = times[ending] - times[starting]
                while current_timespan > self.trim_lightcurve_to_n_days:
                    starting += 1
                    current_timespan = times[ending] - times[starting]
            else:
                starting += 1

        return lightcurve.iloc[best_starting : (best_ending + 1)]

    def compute(self, lightcurve: pd.DataFrame):
        trimmed_lightcurve = self.trim_lightcurve(lightcurve)

        self.periodogram_computer.set_data(
            mjds=np.array(trimmed_lightcurve.mjd),
            mags=np.array(trimmed_lightcurve.brightness),
            errs=np.array(trimmed_lightcurve.e_brightness),
            fids=np.array(trimmed_lightcurve.fid),
        )

        self.periodogram_computer.optimal_frequency_grid_evaluation(
            smallest_period=self.smallest_period,
            largest_period=self.largest_period,
            shift=self.shift,
        )

        self.periodogram_computer.optimal_finetune_best_frequencies(times_finer=10.0, n_local_optima=10)

        best_freq, best_per = self.periodogram_computer.get_best_frequencies()

        freq, score = self.periodogram_computer.get_periodogram()
        period = 1 / freq

        return {
            "period": period.tolist(),
            "score": score.tolist(),
            "best_periods": (1.0 / best_freq).tolist(),
            "best_periods_index": self.periodogram_computer.best_local_optima,
            "best_period": best_per,
        }
