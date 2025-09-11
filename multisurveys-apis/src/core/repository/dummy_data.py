

object_basic_information_dict = {
    "oid": "12",
    "corrected": "Yes",
    "stellar": "Yes", 
    "ndet": 1,
    "count_ndet": 0,
    "firstmjd": 59450.163946799934,
    "lastmjd": 59478.19487270014,
    "meanra": 244.0754619,
    "meandec": 37.6368494,
    "candid": "1234",
    "otherArchives": ['DESI Legacy Survey DR10', 'NED', 'PanSTARRS', 'SDSS DR18', 'SIMBAD', 'TNS', 'Vizier', 'VSX'],
}

tns_data_dict = {
    "object_data": {
        "discoverer": "-",
        "discovery_data_source": { "group_name": "-"},
        "redshift": "-",
    },
    "object_name": "-",
    "object_type": "-"
}

tns_link_str = 'https://www.wis-tns.org/'


classifiers_probabilities_dict = {
    'lc_classifier' :[
        {'class_name': 'SNIa', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.145678, 'ranking': 3, 'order': 1},
        {'class_name': 'SNIbc', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.067890, 'ranking': 8, 'order': 2},
        {'class_name': 'SNII', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.198765, 'ranking': 1, 'order': 3},
        {'class_name': 'SLSN', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.034567, 'ranking': 14, 'order': 4},
        {'class_name': 'QSO', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.123456, 'ranking': 4, 'order': 5},
        {'class_name': 'AGN', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.056789, 'ranking': 10, 'order': 6},
        {'class_name': 'Blazar', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.045678, 'ranking': 12, 'order': 7},
        {'class_name': 'CV/Nova', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.078901, 'ranking': 7, 'order': 8},
        {'class_name': 'YSO', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.112345, 'ranking': 5, 'order': 9},
        {'class_name': 'LPV', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.098765, 'ranking': 6, 'order': 10},
        {'class_name': 'E', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.023456, 'ranking': 15, 'order': 11},
        {'class_name': 'DSCT', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.043210, 'ranking': 13, 'order': 12},
        {'class_name': 'RRL', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.156789, 'ranking': 2, 'order': 13},
        {'class_name': 'CEP', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.062358, 'ranking': 9, 'order': 14},
        {'class_name': 'Periodic-Other', 'classifier_version': 'lc_classifier_1.1.13', 'probability': 0.051234, 'ranking': 11, 'order': 15}
    ],
    'LC_classifier_ATAT_forced_phot': [
        {'class_name': 'SNIa', 'classifier_version': '1.0.1', 'probability': 0.067890, 'ranking': 9, 'order': 1},
        {'class_name': 'SNIbc', 'classifier_version': '1.0.1', 'probability': 0.045678, 'ranking': 15, 'order': 2},
        {'class_name': 'SNIIb', 'classifier_version': '1.0.1', 'probability': 0.123456, 'ranking': 3, 'order': 3},
        {'class_name': 'SNII', 'classifier_version': '1.0.1', 'probability': 0.098765, 'ranking': 5, 'order': 4},
        {'class_name': 'SNIIn', 'classifier_version': '1.0.1', 'probability': 0.034567, 'ranking': 19, 'order': 5},
        {'class_name': 'SLSN', 'classifier_version': '1.0.1', 'probability': 0.056789, 'ranking': 12, 'order': 6},
        {'class_name': 'TDE', 'classifier_version': '1.0.1', 'probability': 0.078901, 'ranking': 7, 'order': 7},
        {'class_name': 'Microlensing', 'classifier_version': '1.0.1', 'probability': 0.112345, 'ranking': 4, 'order': 8},
        {'class_name': 'QSO', 'classifier_version': '1.0.1', 'probability': 0.145678, 'ranking': 2, 'order': 9},
        {'class_name': 'AGN', 'classifier_version': '1.0.1', 'probability': 0.043210, 'ranking': 16, 'order': 10},
        {'class_name': 'Blazar', 'classifier_version': '1.0.1', 'probability': 0.062358, 'ranking': 11, 'order': 11},
        {'class_name': 'YSO', 'classifier_version': '1.0.1', 'probability': 0.051234, 'ranking': 13, 'order': 12},
        {'class_name': 'CV/Nova', 'classifier_version': '1.0.1', 'probability': 0.039876, 'ranking': 17, 'order': 13},
        {'class_name': 'LPV', 'classifier_version': '1.0.1', 'probability': 0.067543, 'ranking': 10, 'order': 14},
        {'class_name': 'EA', 'classifier_version': '1.0.1', 'probability': 0.023456, 'ranking': 22, 'order': 15},
        {'class_name': 'EB/EW', 'classifier_version': '1.0.1', 'probability': 0.034521, 'ranking': 20, 'order': 16},
        {'class_name': 'Periodic-Other', 'classifier_version': '1.0.1', 'probability': 0.045432, 'ranking': 14, 'order': 17},
        {'class_name': 'RSCVn', 'classifier_version': '1.0.1', 'probability': 0.029876, 'ranking': 21, 'order': 18},
        {'class_name': 'CEP', 'classifier_version': '1.0.1', 'probability': 0.156789, 'ranking': 1, 'order': 19},
        {'class_name': 'RRLab', 'classifier_version': '1.0.1', 'probability': 0.087654, 'ranking': 6, 'order': 20},
        {'class_name': 'RRLc', 'classifier_version': '1.0.1', 'probability': 0.076543, 'ranking': 8, 'order': 21},
        {'class_name': 'DSCT', 'classifier_version': '1.0.1', 'probability': 0.037654, 'ranking': 18, 'order': 22}
    ]
}

classifiers_options_dicts = [
    {'lc_classifier': 'Lc Classifier'},
    {'LC_classifier_ATAT_forced_phot': 'Lc Classifier ATAT Forced Phot'},
]
