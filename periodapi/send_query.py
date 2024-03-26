import pandas as pd
import requests
import matplotlib.pyplot as plt


def load_example_curve():
    detections = pd.read_csv('ZTF18abbuive_20240325/detections.csv')
    detections.rename(columns={
        'magpsf_corr': 'brightness',
        'sigmapsf_corr': 'e_brightness'
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
print(detections_json)

r = requests.post('http://localhost:8000/compute_periodogram/', json=detections_json)
print(r.status_code)
print(r.json().keys())
periodogram = r.json()
plt.scatter(periodogram['period'], periodogram['score'])
plt.show()
