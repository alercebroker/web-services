scores = [
        {
            "detector_name": "anomaly_detector",
            "detector_version": "1.0.0",
            "category_name": "Periodic",
            "score": 800,
        },
        {
            "detector_name": "anomaly_detector",
            "detector_version": "1.0.0",
            "category_name": "Stochastic",
            "score": 100,
        },
        {
            "detector_name": "anomaly_detector",
            "detector_version": "1.0.0",
            "category_name": "Transient",
            "score": 356,
        },
    ]

distributions = [
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Transient",
        "distribution_name": "percentil_10",
        "distribution_version": "1.0.0",
        "distribution_value": 33,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Transient",
        "distribution_name": "percentil_50",
        "distribution_version": "1.0.0",
        "distribution_value": 78,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Transient",
        "distribution_name": "percentil_90",
        "distribution_version": "1.0.0",
        "distribution_value": 345,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Transient",
        "distribution_name": "saturation",
        "distribution_version": "1.0.0",
        "distribution_value": 400,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Periodic",
        "distribution_name": "percentil_10",
        "distribution_version": "1.0.0",
        "distribution_value": 99,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Periodic",
        "distribution_name": "percentil_50",
        "distribution_version": "1.0.0",
        "distribution_value": 240,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Periodic",
        "distribution_name": "percentil_90",
        "distribution_version": "1.0.0",
        "distribution_value": 500,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Periodic",
        "distribution_name": "saturation",
        "distribution_version": "1.0.0",
        "distribution_value": 550,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Stochastic",
        "distribution_name": "percentil_10",
        "distribution_version": "1.0.0",
        "distribution_value": 40,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Stochastic",
        "distribution_name": "percentil_50",
        "distribution_version": "1.0.0",
        "distribution_value": 210,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Stochastic",
        "distribution_name": "percentil_90",
        "distribution_version": "1.0.0",
        "distribution_value": 280,
    },
    {
        "detector_name": "anomaly_detector",
        "detector_version": "1.0.0",
        "category_name": "Stochastic",
        "distribution_name": "saturation",
        "distribution_version": "1.0.0",
        "distribution_value": 300,
    },
]

table_rows = []

def str_separator(word):

    if word == 'saturation':
        return float(100)
    else:
        return float(word.split('_')[1])

for dic in range(len(scores)):

    current_category = scores[dic]['category_name']
    current_score = float(scores[dic]['score'])

    flag = 0

    for dist in range(len(distributions)):

        if distributions[dist]['category_name'] == current_category:
            if flag == 0:
                print(current_score)
                print(distributions[dist]['distribution_value'])
                if current_score < float(distributions[dist]['distribution_value']):
                    flag = 1
                    def_value = distributions[dist]['distribution_value']
                    def_index = dist
    
        if flag == 1:
            break
    
    if flag == 1:
        percentil = str_separator(distributions[def_index]['distribution_name'])
    else: 
        percentil = 0
        def_value = None 

    table_rows.append({'category': current_category, 'score': current_score, 'decil': def_value, 'percentil': percentil})

    print(table_rows)