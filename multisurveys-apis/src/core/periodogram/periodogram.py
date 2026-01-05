from lightcurve_api.models.periodogram import Periodogram
import numpy as np
import pandas as pd
import pprint
from P4J import MultiBandPeriodogram
from scipy.stats import f


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

    def optimal_frequency_grid_evaluation(self, smallest_period, largest_period, shift):

        lc_time_length = self.periodogram_computer.get_lc_time_length()
        smallest_frequency = 1.0/largest_period
        largest_frequency = 1.0/smallest_period
        f_range = largest_frequency - smallest_frequency
        grid_size = int(np.ceil(f_range * lc_time_length / (2.0 * shift)))
        grid_size = max(grid_size, 1_000)
        self.periodogram_computer.freq_step_coarse = f_range / (grid_size - 1)

        frequency_grid = np.logspace(
            smallest_frequency,
            largest_frequency,
            grid_size,
            dtype=np.float32
        )

        self.periodogram_computer.per, self.periodogram_computer.per_single_band = self.periodogram_computer._compute_periodogram(frequency_grid)

        self.periodogram_computer.freq = frequency_grid


    def compute(self, lightcurve: pd.DataFrame):
        trimmed_lightcurve = self.trim_lightcurve(lightcurve)

        self.periodogram_computer.set_data(
            mjds=np.array(trimmed_lightcurve.mjd),
            mags=np.array(trimmed_lightcurve.brightness),
            errs=np.array(trimmed_lightcurve.e_brightness),
            fids=np.array(trimmed_lightcurve.fid),
        )


        self.optimal_frequency_grid_evaluation(
            smallest_period=self.smallest_period,
            largest_period=self.largest_period,
            shift=self.shift,
        )

        self.periodogram_computer.optimal_finetune_best_frequencies(times_finer=10.0, n_local_optima=10)

        best_freq, _ = self.periodogram_computer.get_best_frequencies()

        freq, score = self.periodogram_computer.get_periodogram()
        period = 1 / freq

        local_optima = (
            [self.periodogram_computer.best_local_optima]
            if isinstance(self.periodogram_computer.best_local_optima, int)
            else self.periodogram_computer.best_local_optima
        )

        return Periodogram(
            periods=period.tolist(),
            scores=score.tolist(),
            best_periods=(1.0 / best_freq).tolist(),
            best_periods_index=local_optima,
        )
