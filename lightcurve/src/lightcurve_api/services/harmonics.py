import numpy as np
import pandas as pd


def compute_chi_squared(lightcurve_with_period):
    n_harmonics = 7
    degrees_of_freedom = n_harmonics * 2 + 1
    error_tol = 1e-2
    period = lightcurve_with_period.period
    # period = lightcurve_with_period['period']

    observations = pd.DataFrame(
        data=np.stack(
            [
                lightcurve_with_period.mjd,
                lightcurve_with_period.brightness,
                lightcurve_with_period.e_brightness,
                lightcurve_with_period.fid,
            ],
            axis=1,
        ),
        # data=np.stack([
        #     lightcurve_with_period['mjd'],
        #     lightcurve_with_period['brightness'],
        #     lightcurve_with_period['e_brightness'],
        #     lightcurve_with_period['fid']
        # ], axis=1),
        columns=[["mjd", "brightness", "e_brightness", "fid"]],
    )

    chis = []
    for band in ["g", "r"]:
        band_observations = observations[(observations["fid"] == band).values]
        print(band_observations)
        if len(band_observations) < degrees_of_freedom:
            continue

        time = band_observations["mjd"].astype(np.float64).values.flatten()
        brightness = (
            band_observations["brightness"].astype(np.float64).values.flatten()
        )
        error = (
            band_observations["e_brightness"]
            .astype(np.float64)
            .values.flatten()
            + 10**-2
        )

        best_freq = 1 / period

        omega = [np.array([[1.0] * len(time)])]
        timefreq = (
            2.0 * np.pi * best_freq * np.arange(1, n_harmonics + 1)
        ).reshape(1, -1).T * time
        omega.append(np.cos(timefreq))
        omega.append(np.sin(timefreq))

        # Omega.shape == (lc_length, 1+2*self.n_harmonics)
        omega = np.concatenate(omega, axis=0).T
        inverr = 1.0 / error

        # weighted regularized linear regression
        w_a = inverr.reshape(-1, 1) * omega
        w_b = (brightness * inverr).reshape(-1, 1)
        coeffs = np.matmul(np.linalg.pinv(w_a), w_b).flatten()
        fitted_magnitude = np.dot(omega, coeffs)

        # Calculate reduced chi-squared statistic
        chi = np.sum(
            (fitted_magnitude - brightness) ** 2 / (error + error_tol) ** 2
        )
        chi_den = len(fitted_magnitude) - (1 + 2 * n_harmonics)
        if chi_den >= 1:
            chi_per_degree = chi / chi_den
            chis.append(chi_per_degree)

    if len(chis) == 0:
        return 999.0
    else:
        print(chis)
        return np.mean(chis)
