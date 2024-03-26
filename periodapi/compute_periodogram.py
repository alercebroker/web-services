from P4J import MultiBandPeriodogram
import numpy as np


class PeriodogramComputer:
    def __init__(self):
        self.periodogram_computer = MultiBandPeriodogram(method='MHAOV')
        self.smallest_period = 0.05
        self.largest_period = 500.0
        self.min_length = 1500
        self.shift = 0.1

    def compute(self, lightcurve):
        self.periodogram_computer.set_data(
            mjds=np.array(lightcurve.mjd),
            mags=np.array(lightcurve.brightness),
            errs=np.array(lightcurve.e_brightness),
            fids=np.array(lightcurve.fid))

        self.periodogram_computer.optimal_frequency_grid_evaluation(
            smallest_period=self.smallest_period,
            largest_period=self.largest_period,
            shift=self.shift
        )

        self.periodogram_computer.optimal_finetune_best_frequencies(
            times_finer=10.0, n_local_optima=10)

        best_freq, best_per = self.periodogram_computer.get_best_frequencies()

        if len(best_freq) == 0:
            print('[PeriodExtractor] best frequencies has len 0')

        freq, score = self.periodogram_computer.get_periodogram()
        period = 1/freq

        return {
            'period': period.tolist(),
            'score': score.tolist(),
            'best_periods': (1.0/best_freq).tolist(),
            'best_periods_index': self.periodogram_computer.best_local_optima.tolist()
        }
