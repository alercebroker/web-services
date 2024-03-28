import pandas as pd
import requests
import matplotlib.pyplot as plt
# from harmonics import compute_chi_squared


def load_example_curve():
    detections = pd.read_csv('ZTF18abbuive_20240325/detections.csv')
    detections.rename(columns={
        'magpsf_corr': 'brightness',
        'sigmapsf_corr_ext': 'e_brightness'
    }, inplace=True)
    detections = detections[detections['e_brightness'] < 1.0]
    return detections


detections = load_example_curve()
detections_json = {
    'mjd': detections['mjd'].values.tolist(),
    'brightness': detections['brightness'].values.tolist(),
    'e_brightness': detections['e_brightness'].values.tolist(),
    'fid': detections['fid'].map({1: "g", 2: "r"}).values.tolist()
}


detections_with_period = {
    'mjd': detections['mjd'].values.tolist(),
    'brightness': detections['brightness'].values.tolist(),
    'e_brightness': detections['e_brightness'].values.tolist(),
    'fid': detections['fid'].map({1: "g", 2: "r"}).values.tolist(),
    'period': 0.60835  # 0.60829
}

# compute_chi_squared(detections_with_period)

r = requests.post('http://ec2-54-162-233-91.compute-1.amazonaws.com/compute_periodogram/', json=detections_json)
print(r.status_code)
print(r.json().keys())


r2 = requests.post('http://ec2-54-162-233-91.compute-1.amazonaws.com/chi_squared/', json=detections_with_period)
print(r2.json())

periodogram = r.json()
plt.scatter(periodogram['period'], periodogram['score'])
plt.semilogx()
plt.xlabel('Period [days]')
plt.title(f'Best period {periodogram["best_periods"][0]:.3f}')
plt.show()
