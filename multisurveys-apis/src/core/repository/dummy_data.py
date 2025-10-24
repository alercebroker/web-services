import random
import time


object_basic_information_dict = {
    "oid": "12",  # si
    "corrected": "Yes",  # si
    "stellar": "Yes",  # si
    "ndet": 1,  # si
    "count_ndet": 0,
    "firstmjd": 59450.163946799934,  # si
    "lastmjd": 59478.19487270014,  # si
    "meanra": 244.0754619,  # si
    "meandec": 37.6368494,  # si
    "measurement_id": 1234,
    "otherArchives": ["DESI Legacy Survey DR10", "NED", "PanSTARRS", "SDSS DR18", "SIMBAD", "TNS", "Vizier", "VSX"],
}

magstats_dummy = [
    {
        "fid": 1,
        "stellar": False,
        "corrected": False,
        "ndet": 38,
        "ndubious": 0,
        "magmean": 19.255001,
        "magmedian": 19.349136,
        "magmax": 20.2086,
        "magmin": 18.587002,
        "magsigma": 0.41979843,
        "maglast": 20.2086,
        "magfirst": 18.776695,
        "firstmjd": 59140.406,
        "lastmjd": 59260.14,
        "step_id_corr": "correction_0.0.1",
    },
    {
        "fid": 2,
        "stellar": False,
        "corrected": False,
        "ndet": 40,
        "ndubious": 0,
        "magmean": 18.685757,
        "magmedian": 18.596018,
        "magmax": 19.732458,
        "magmin": 18.37707,
        "magsigma": 0.28526792,
        "maglast": 19.732458,
        "magfirst": 18.89238,
        "firstmjd": 59140.258,
        "lastmjd": 59267.145,
        "step_id_corr": "correction_0.0.1",
    },
]

tns_data_dict = {
    "object_data": {
        "discoverer": "-",
        "discovery_data_source": {"group_name": "-"},
        "redshift": "-",
    },
    "object_name": "-",
    "object_type": "-",
}

tns_link_str = "https://www.wis-tns.org/"

crossmatch_dummy = [
    {
        "2MASS": {
            "Dec": {"unit": "deg", "value": 16.763382},
            "Epoch": {"unit": "JD", "value": 2451079.6739},
            "ErrMaj": {"unit": "arcsec", "value": 0.07},
            "MagErr_H": {"unit": "mag", "value": 0.041},
            "MagErr_J": {"unit": "mag", "value": 0.016},
            "MagErr_K": {"unit": "mag", "value": 0.027},
            "Mag_H": {"unit": "mag", "value": 8.156},
            "Mag_J": {"unit": "mag", "value": 9.078},
            "Mag_K": {"unit": "mag", "value": 7.767},
            "RA": {"unit": "deg", "value": 303.287252},
            "distance": {"unit": "arcsec", "value": 0.27889557708910884},
        }
    },
    {
        "GAIA/DR1": {
            "Dec": {"unit": "deg", "value": 16.76280935462812},
            "ErrDec": {"unit": "mas", "value": 1.7319820487594266},
            "ErrMagG": {"unit": "mag", "value": 0.009472408518078006},
            "ErrRA": {"unit": "mas", "value": 2.6765492427558586},
            "ExcessNoise": {"unit": " ", "value": 1.8785793234102481},
            "ExcessNoiseSig": {"unit": " ", "value": 2.702725363894997},
            "MagG": {"unit": "mag", "value": 19.35988898297645},
            "RA": {"unit": "deg", "value": 303.2893235568486},
            "distance": {"unit": "arcsec", "value": 7.392039386518965},
        }
    },
    {
        "GAIA/DR2": {
            "A_G": {"unit": "mag", "value": 1.9693},
            "Dec": {"unit": "deg", "value": 16.76334485229528},
            "Epoch": {"unit": "JYear", "value": 2015.5},
            "ErrDec": {"unit": "mas", "value": 0.05599270543749009},
            "ErrPMDec": {"unit": "mas/yr", "value": 0.13220718052818284},
            "ErrPMRA": {"unit": "mas/yr", "value": 0.19181906827117712},
            "ErrPlx": {"unit": "mas", "value": 0.1442836669705719},
            "ErrRA": {"unit": "mas", "value": 0.09282778037153405},
            "ErrRV": {"unit": "km/s", "value": None},
            "ExcessNoise": {"unit": "mas", "value": 0.8635385668101555},
            "ExcessNoiseSig": {"unit": " ", "value": 298.17118669906296},
            "MagErr_BP": {"unit": "mag", "value": 0.02725674422456947},
            "MagErr_G": {"unit": "mag", "value": 0.002463521954426749},
            "MagErr_RP": {"unit": "mag", "value": 0.006593173624731371},
            "Mag_BP": {"unit": "mag", "value": 15.856002},
            "Mag_G": {"unit": "mag", "value": 13.081091},
            "Mag_RP": {"unit": "mag", "value": 11.596178},
            "PMDec": {"unit": "mas/yr", "value": -5.52464090055739},
            "PMRA": {"unit": "mas/yr", "value": -3.454541061375139},
            "Plx": {"unit": "mas", "value": 0.25399846813711124},
            "RA": {"unit": "deg", "value": 303.2872381286785},
            "RA_Dec_Corr": {"unit": " ", "value": -0.28280157},
            "RV": {"unit": "km/s", "value": None},
            "Teff": {"unit": "K", "value": 3284.0},
            "Teff_high": {"unit": "K", "value": 3375.0},
            "Teff_low": {"unit": "K", "value": 3275.0},
            "VarFlag": {"unit": " ", "value": 1.0},
            "distance": {"unit": "arcsec", "value": 0.14403583509092927},
        }
    },
    {
        "APASS": {
            "B": {"unit": "mag", "value": 15.358},
            "BV": {"unit": "mag", "value": 1.558},
            "BVerr": {"unit": "mag", "value": 0.047},
            "Berr": {"unit": "mag", "value": 0.047},
            "Dec": {"unit": "deg", "value": 16.771044},
            "Decerr": {"unit": "arcsec", "value": 1.015},
            "Mobs": {"unit": " ", "value": 7.0},
            "Name": {"unit": " ", "value": 20120911.0},
            "Nobs": {"unit": " ", "value": 2.0},
            "RA": {"unit": "deg", "value": 303.286215},
            "RAerr": {"unit": "arcsec", "value": 1.551},
            "V": {"unit": "mag", "value": 13.8},
            "Verr": {"unit": "mag", "value": -0.0},
            "distance": {"unit": "arcsec", "value": 28.084398414811314},
            "g": {"unit": "mag", "value": 14.59},
            "gerr": {"unit": "mag", "value": -0.0},
            "i": {"unit": "mag", "value": 12.932},
            "ierr": {"unit": "mag", "value": 0.022},
            "r": {"unit": "mag", "value": 13.368},
            "rerr": {"unit": "mag", "value": -0.0},
        }
    },
    {
        "UCAC4": {
            "DSflag": {"unit": " ", "value": 0.0},
            "Dec": {"unit": "deg", "value": 16.763375277777776},
            "EpochDec": {"unit": "year", "value": 2001.02},
            "EpochRA": {"unit": "year", "value": 2000.95},
            "ErrDec": {"unit": "mas", "value": 25.0},
            "ErrMag": {"unit": "mag", "value": 0.12},
            "ErrMagB": {"unit": "mag", "value": -0.08},
            "ErrMagH": {"unit": "mag", "value": 0.04},
            "ErrMagJ": {"unit": "mag", "value": 0.02},
            "ErrMagK": {"unit": "mag", "value": 0.03},
            "ErrMagV": {"unit": "mag", "value": -0.01},
            "ErrMagg": {"unit": "mag", "value": None},
            "ErrMagi": {"unit": "mag", "value": -0.01},
            "ErrMagr": {"unit": "mag", "value": None},
            "ErrPM_Dec": {"unit": "mas/yr", "value": 5.0},
            "ErrPM_RA": {"unit": "mas/yr", "value": 5.9},
            "ErrRA": {"unit": "mas", "value": 32.0},
            "Flag2MASSext": {"unit": " ", "value": 0.0},
            "FlagExtCat": {"unit": " ", "value": 10.0},
            "FlagH": {"unit": " ", "value": 45.0},
            "FlagJ": {"unit": " ", "value": 5.0},
            "FlagK": {"unit": " ", "value": 5.0},
            "FlagLEDA": {"unit": " ", "value": 0.0},
            "FlagYale": {"unit": " ", "value": 0.0},
            "ID": {"unit": " ", "value": 124018603.0},
            "ID2MASS": {"unit": " ", "value": 339659815.0},
            "MagAper": {"unit": "mag", "value": 14.826},
            "MagB": {"unit": "mag", "value": 16.578},
            "MagH": {"unit": "mag", "value": 8.156},
            "MagJ": {"unit": "mag", "value": 9.078},
            "MagK": {"unit": "mag", "value": 7.767},
            "MagModel": {"unit": "mag", "value": 14.805},
            "MagV": {"unit": "mag", "value": 15.043},
            "Magg": {"unit": "mag", "value": None},
            "Magi": {"unit": "mag", "value": 12.086},
            "Magr": {"unit": "mag", "value": None},
            "Nep": {"unit": " ", "value": 2.0},
            "Nim": {"unit": " ", "value": 3.0},
            "Nobs": {"unit": " ", "value": 3.0},
            "ObjType": {"unit": " ", "value": 0.0},
            "PM_Dec": {"unit": "mas/yr", "value": 2.3},
            "PM_RA": {"unit": "mas/yr", "value": 4.0},
            "RA": {"unit": "deg", "value": 303.28725638888886},
            "RecordUCAC2": {"unit": " ", "value": 148288.0},
            "ZoneUCAC2": {"unit": " ", "value": 214.0},
            "distance": {"unit": "arcsec", "value": 0.2572569897789975},
        }
    },
    {
        "WISE": {
            "Dec": {"unit": "deg", "value": 16.7633654},
            "Dist_2MASS": {"unit": "arcsec", "value": 0.06},
            "ErrDec": {"unit": "arcse", "value": 0.0635},
            "ErrRA": {"unit": "arcsec", "value": 0.0629},
            "MagErr_H": {"unit": "mag", "value": 0.044},
            "MagErr_J": {"unit": "mag", "value": 0.02},
            "MagErr_K": {"unit": "mag", "value": 0.031},
            "MagErr_W1": {"unit": "mag", "value": 0.027},
            "MagErr_W2": {"unit": "mag", "value": 0.021},
            "MagErr_W3": {"unit": "mag", "value": 0.016},
            "MagErr_W4": {"unit": "mag", "value": 0.042},
            "Mag_H": {"unit": "mag", "value": 8.156},
            "Mag_J": {"unit": "mag", "value": 9.078},
            "Mag_K": {"unit": "mag", "value": 7.767},
            "Mag_W1": {"unit": "mag", "value": 7.584},
            "Mag_W2": {"unit": "mag", "value": 7.442},
            "Mag_W3": {"unit": "mag", "value": 6.59},
            "Mag_W4": {"unit": "mag", "value": 5.804},
            "MeanMJD_W1": {"unit": "MJD", "value": 55316.59656812},
            "PA_2MASS": {"unit": "deg", "value": -0.3},
            "RA": {"unit": "deg", "value": 303.2872521},
            "RChi2_W1": {"unit": " ", "value": 0.748300016},
            "RChi2_W2": {"unit": " ", "value": 0.641799986},
            "RChi2_W3": {"unit": " ", "value": 1.00399995},
            "RChi2_W4": {"unit": " ", "value": 1.01300001},
            "SNR_W1": {"unit": " ", "value": 40.5},
            "SNR_W2": {"unit": " ", "value": 50.5},
            "SNR_W3": {"unit": " ", "value": 67.9},
            "SNR_W4": {"unit": " ", "value": 26.0},
            "Sky_W1": {"unit": "DN", "value": 16.622},
            "Sky_W2": {"unit": "DN", "value": 34.285},
            "Sky_W3": {"unit": "DN", "value": 1755.606},
            "Sky_W4": {"unit": "DN", "value": 513.684},
            "VarL_W1": {"unit": " ", "value": 0.0},
            "VarL_W2": {"unit": " ", "value": 0.0},
            "VarL_W3": {"unit": " ", "value": 0.0},
            "VarL_W4": {"unit": " ", "value": 0.0},
            "distance": {"unit": "arcsec", "value": 0.21971106196804413},
        }
    },
    {
        "AAVSO_VSX": {
            "Dec": {"unit": "deg", "value": 16.763369999999995},
            "Epoch": {"unit": "d", "value": 2457694.8},
            "MaxMag": {"unit": "mag", "value": 14.760000228881836},
            "MinMag": {"unit": "mag", "value": 15.600000381469727},
            "RA": {"unit": "deg", "value": 303.28729999999996},
            "VarFlag": {"unit": " ", "value": 0.0},
            "distance": {"unit": "arcsec", "value": 0.3064552158885286},
            "period": {"unit": "d", "value": 91.6},
        }
    },
    {
        "unWISE": {
            "Dec": {"unit": "deg", "value": 16.763347413415595},
            "ErrMag_w1": {"unit": "magAB", "value": 0.0007091392643473717},
            "ErrMag_w2": {"unit": "magAB", "value": 0.0017016126237245999},
            "FlagsAdd_w1": {"unit": " ", "value": 24.0},
            "FlagsAdd_w2": {"unit": " ", "value": 24.0},
            "Flags_w1": {"unit": " ", "value": 97.0},
            "Flags_w2": {"unit": " ", "value": 33.0},
            "MagAB_w1": {"unit": "magAB", "value": 10.385646273781735},
            "MagAB_w2": {"unit": "magAB", "value": 10.806421232647816},
            "N_w1": {"unit": " ", "value": 19.0},
            "N_w2": {"unit": " ", "value": 156.0},
            "RA": {"unit": "deg", "value": 303.2871981899522},
            "SkyMag_w1": {"unit": "magAB", "value": 22.326384295238448},
            "SkyMag_w2": {"unit": "magAB", "value": 23.379389376043004},
            "distance": {"unit": "arcsec", "value": 0.21584184851255825},
        }
    },
]


classifiers_probabilities_dict = {
    "lc_classifier": [
        {
            "class_name": "SNIa",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.145678,
            "ranking": 3,
            "order": 1,
        },
        {
            "class_name": "SNIbc",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.067890,
            "ranking": 8,
            "order": 2,
        },
        {
            "class_name": "SNII",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.198765,
            "ranking": 1,
            "order": 3,
        },
        {
            "class_name": "SLSN",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.034567,
            "ranking": 14,
            "order": 4,
        },
        {
            "class_name": "QSO",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.123456,
            "ranking": 4,
            "order": 5,
        },
        {
            "class_name": "AGN",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.056789,
            "ranking": 10,
            "order": 6,
        },
        {
            "class_name": "Blazar",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.045678,
            "ranking": 12,
            "order": 7,
        },
        {
            "class_name": "CV/Nova",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.078901,
            "ranking": 7,
            "order": 8,
        },
        {
            "class_name": "YSO",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.112345,
            "ranking": 5,
            "order": 9,
        },
        {
            "class_name": "LPV",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.098765,
            "ranking": 6,
            "order": 10,
        },
        {
            "class_name": "E",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.023456,
            "ranking": 15,
            "order": 11,
        },
        {
            "class_name": "DSCT",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.043210,
            "ranking": 13,
            "order": 12,
        },
        {
            "class_name": "RRL",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.156789,
            "ranking": 2,
            "order": 13,
        },
        {
            "class_name": "CEP",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.062358,
            "ranking": 9,
            "order": 14,
        },
        {
            "class_name": "Periodic-Other",
            "classifier_version": "lc_classifier_1.1.13",
            "probability": 0.051234,
            "ranking": 11,
            "order": 15,
        },
    ],
    "LC_classifier_ATAT_forced_phot": [
        {"class_name": "SNIa", "classifier_version": "1.0.1", "probability": 0.067890, "ranking": 9, "order": 1},
        {"class_name": "SNIbc", "classifier_version": "1.0.1", "probability": 0.045678, "ranking": 15, "order": 2},
        {"class_name": "SNIIb", "classifier_version": "1.0.1", "probability": 0.123456, "ranking": 3, "order": 3},
        {"class_name": "SNII", "classifier_version": "1.0.1", "probability": 0.098765, "ranking": 5, "order": 4},
        {"class_name": "SNIIn", "classifier_version": "1.0.1", "probability": 0.034567, "ranking": 19, "order": 5},
        {"class_name": "SLSN", "classifier_version": "1.0.1", "probability": 0.056789, "ranking": 12, "order": 6},
        {"class_name": "TDE", "classifier_version": "1.0.1", "probability": 0.078901, "ranking": 7, "order": 7},
        {
            "class_name": "Microlensing",
            "classifier_version": "1.0.1",
            "probability": 0.112345,
            "ranking": 4,
            "order": 8,
        },
        {"class_name": "QSO", "classifier_version": "1.0.1", "probability": 0.145678, "ranking": 2, "order": 9},
        {"class_name": "AGN", "classifier_version": "1.0.1", "probability": 0.043210, "ranking": 16, "order": 10},
        {"class_name": "Blazar", "classifier_version": "1.0.1", "probability": 0.062358, "ranking": 11, "order": 11},
        {"class_name": "YSO", "classifier_version": "1.0.1", "probability": 0.051234, "ranking": 13, "order": 12},
        {"class_name": "CV/Nova", "classifier_version": "1.0.1", "probability": 0.039876, "ranking": 17, "order": 13},
        {"class_name": "LPV", "classifier_version": "1.0.1", "probability": 0.067543, "ranking": 10, "order": 14},
        {"class_name": "EA", "classifier_version": "1.0.1", "probability": 0.023456, "ranking": 22, "order": 15},
        {"class_name": "EB/EW", "classifier_version": "1.0.1", "probability": 0.034521, "ranking": 20, "order": 16},
        {
            "class_name": "Periodic-Other",
            "classifier_version": "1.0.1",
            "probability": 0.045432,
            "ranking": 14,
            "order": 17,
        },
        {"class_name": "RSCVn", "classifier_version": "1.0.1", "probability": 0.029876, "ranking": 21, "order": 18},
        {"class_name": "CEP", "classifier_version": "1.0.1", "probability": 0.156789, "ranking": 1, "order": 19},
        {"class_name": "RRLab", "classifier_version": "1.0.1", "probability": 0.087654, "ranking": 6, "order": 20},
        {"class_name": "RRLc", "classifier_version": "1.0.1", "probability": 0.076543, "ranking": 8, "order": 21},
        {"class_name": "DSCT", "classifier_version": "1.0.1", "probability": 0.037654, "ranking": 18, "order": 22},
    ],
}

classifiers_options_dicts = [
    {"lc_classifier": "Lc Classifier"},
    {"LC_classifier_ATAT_forced_phot": "Lc Classifier ATAT Forced Phot"},
]


def generate_array_dicts_data_table(n=20, seed=None):
    rnd = random.Random(seed if seed is not None else time.time_ns())
    base_oid = rnd.randint(10000, 99999)

    rows = []
    for i in range(n):
        oid = f"{base_oid + i}"
        n_det = rnd.randint(5, 45)
        firstmjd = 57900.0 + rnd.uniform(0, 200)
        lastmjd = firstmjd + rnd.uniform(10, 200)
        meanra = round(rnd.uniform(0, 360), 5)
        meandec = round(rnd.uniform(-90, 90), 5)
        probability = round(rnd.uniform(0.5, 0.99), 2)

        rows.append({
            'oid': oid,
            'n_det': n_det,
            'firstmjd': round(firstmjd, 3),
            'lastmjd': round(lastmjd, 3),
            'meanra': meanra,
            'meandec': meandec,
            'Probability': probability
        })
    return rows


objects_dummy = [
    {
        "oid": "ZTF20acobvxk", "ndethist": "102", "ncovhist": 502, "mjdstarthist": 59149.44812500011,
        "mjdendhist": 59204.1988309999, "corrected": False, "stellar": False, "ndet": 37,
        "g_r_max": -0.18531418, "g_r_max_corr": 0.5885992, "g_r_mean": 0.07172012, "g_r_mean_corr": 0.6859235,
        "firstmjd": 59149.44812500011, "lastmjd": 59204.1988309999, "deltajd": 54.7507059997879,
        "meanra": 37.67353272162162, "meandec": -14.569120659459461, "sigmara": 0.00007960835430402907,
        "sigmadec": 0.000059398192356675655, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.722, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF22aalpfln", "ndethist": "59", "ncovhist": 2921, "mjdstarthist": 59724.25,
        "mjdendhist": 59766.25, "corrected": False, "stellar": False, "ndet": 28,
        "g_r_max": -0.17975, "g_r_max_corr": None, "g_r_mean": 0.17018412, "g_r_mean_corr": None,
        "firstmjd": 59724.34915510006, "lastmjd": 59766.241782399826, "deltajd": 41.89262729976326,
        "meanra": 224.50374205714283, "meandec": 49.95310938214286, "sigmara": 0.00004943191672873918,
        "sigmadec": 0.000022054730803539187, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.722, "step_id_corr": "dev"
    },
    {
        "oid": "ZTF21abuyhau", "ndethist": "53", "ncovhist": 2702, "mjdstarthist": 59448.18409720017,
        "mjdendhist": 59478.19487270014, "corrected": False, "stellar": False, "ndet": 28,
        "g_r_max": -0.18009, "g_r_max_corr": 0.486082, "g_r_mean": -0.07121199, "g_r_mean_corr": 1.1913389,
        "firstmjd": 59450.163946799934, "lastmjd": 59478.19487270014, "deltajd": 28.030925900209695,
        "meanra": 244.0754618535714, "meandec": 37.636849425, "sigmara": 0.00006440991114382217,
        "sigmadec": 0.00003236927698537371, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.72, "step_id_corr": "correction_1.0.6"
    },
    {
        "oid": "ZTF21abywdxt", "ndethist": "44", "ncovhist": 1171, "mjdstarthist": 59464.26791669987,
        "mjdendhist": 59502.20440969989, "corrected": False, "stellar": False, "ndet": 27,
        "g_r_max": -0.098903, "g_r_max_corr": None, "g_r_mean": 0.02477162, "g_r_mean_corr": None,
        "firstmjd": 59465.1969444002, "lastmjd": 59502.20440969989, "deltajd": 37.007465299684554,
        "meanra": 326.5036098666667, "meandec": 21.962613925925925, "sigmara": 0.00002514084939155159,
        "sigmadec": 0.000023029155310617024, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.716564, "step_id_corr": "correction_1.0.6"
    },
    {
        "oid": "ZTF22abqdmwt", "ndethist": "28", "ncovhist": 699, "mjdstarthist": 59877.25,
        "mjdendhist": 59932.25, "corrected": False, "stellar": False, "ndet": 21,
        "g_r_max": -0.086032, "g_r_max_corr": None, "g_r_mean": 0.00939528, "g_r_mean_corr": None,
        "firstmjd": 59878.3104514, "lastmjd": 59932.21045139991, "deltajd": 53.89999999990687,
        "meanra": 28.288161904761907, "meandec": -14.140190614285714, "sigmara": 0.000040297214248849656,
        "sigmadec": 0.00005195567616435475, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.714568, "step_id_corr": "1.1.6"
    },
    {
        "oid": "ZTF23abcegjv", "ndethist": "27", "ncovhist": 2776, "mjdstarthist": 60198.25,
        "mjdendhist": 60237.25, "corrected": False, "stellar": False, "ndet": 25,
        "g_r_max": 0.071632, "g_r_max_corr": None, "g_r_mean": 0.2615823, "g_r_mean_corr": None,
        "firstmjd": 60198.20725690015, "lastmjd": 60237.153506900184, "deltajd": 38.94625000003725,
        "meanra": 265.70668244800004, "meandec": 18.658192724, "sigmara": 0.000021072476519615275,
        "sigmadec": 0.00003895863490082146, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.714, "step_id_corr": "1.2.1"
    },
    {
        "oid": "ZTF21abufayv", "ndethist": "129", "ncovhist": 1744, "mjdstarthist": 59443.32858800003,
        "mjdendhist": 59491.2366204001, "corrected": False, "stellar": False, "ndet": 30,
        "g_r_max": -0.00098, "g_r_max_corr": None, "g_r_mean": 0.12838416, "g_r_mean_corr": None,
        "firstmjd": 59446.395393500105, "lastmjd": 59491.235682900064, "deltajd": 44.84028939995915,
        "meanra": 12.033976029999998, "meandec": 24.44080683666667, "sigmara": 0.00003088251541922917,
        "sigmadec": 0.00002581163174464046, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.712, "step_id_corr": "correction_1.0.6"
    },
    {
        "oid": "ZTF21achqzub", "ndethist": "60", "ncovhist": 1557, "mjdstarthist": 59502.2983448999,
        "mjdendhist": 59543.12950230017, "corrected": False, "stellar": False, "ndet": 22,
        "g_r_max": -0.09135, "g_r_max_corr": None, "g_r_mean": 0.00445514, "g_r_mean_corr": None,
        "firstmjd": 59502.35163189983, "lastmjd": 59543.128564800136, "deltajd": 40.77693290030584,
        "meanra": 351.3827864227273, "meandec": 18.37406694090909, "sigmara": 0.000010695256258065284,
        "sigmadec": 0.000009194286999278764, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.71, "step_id_corr": "correction_1.0.6"
    },
    {
        "oid": "ZTF22abnemvx", "ndethist": "80", "ncovhist": 1549, "mjdstarthist": 59866.5,
        "mjdendhist": 59914.5, "corrected": True, "stellar": False, "ndet": 29,
        "g_r_max": -0.143576, "g_r_max_corr": -0.128327, "g_r_mean": 0.22535884, "g_r_mean_corr": 0.18847026,
        "firstmjd": 59866.4656134001, "lastmjd": 59914.4054744998, "deltajd": 47.939861099701375,
        "meanra": 141.16020438965518, "meandec": 39.136804986206904, "sigmara": 0.00007845531187164709,
        "sigmadec": 0.00003855062278693585, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.706, "step_id_corr": "1.1.6"
    },
    {
        "oid": "ZTF20acoqlav", "ndethist": "23", "ncovhist": 1097, "mjdstarthist": 58837.1098842998,
        "mjdendhist": 59199.13137729978, "corrected": False, "stellar": False, "ndet": 23,
        "g_r_max": -0.057519913, "g_r_max_corr": 0.54309076, "g_r_mean": -0.09345436, "g_r_mean_corr": 0.62354934,
        "firstmjd": 59153.23980320012, "lastmjd": 59199.13137729978, "deltajd": 45.89157409965992,
        "meanra": 1.7899487652173918, "meandec": 39.17106486086956, "sigmara": 0.000062540762043631,
        "sigmadec": 0.0000912397229039402, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.70432, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF23aaedsfn", "ndethist": "22", "ncovhist": 1369, "mjdstarthist": 60036.25,
        "mjdendhist": 60073.25, "corrected": False, "stellar": False, "ndet": 20,
        "g_r_max": -0.079873, "g_r_max_corr": None, "g_r_mean": 0.018690951, "g_r_mean_corr": None,
        "firstmjd": 60036.2062615999, "lastmjd": 60073.17984949984, "deltajd": 36.9735878999345,
        "meanra": 130.10592426000002, "meandec": 71.95604784, "sigmara": 0.00007334123130917731,
        "sigmadec": 0.000020058635101290745, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.704, "step_id_corr": "1.2.0"
    },
    {
        "oid": "ZTF19aavounq", "ndethist": "32", "ncovhist": 157, "mjdstarthist": 58632.272465299815,
        "mjdendhist": 58690.171747699846, "corrected": False, "stellar": False, "ndet": 28,
        "g_r_max": -0.17508316, "g_r_max_corr": None, "g_r_mean": -0.14762688, "g_r_mean_corr": None,
        "firstmjd": 58632.272465299815, "lastmjd": 58690.171747699846, "deltajd": 57.89928240003064,
        "meanra": 227.49142044285713, "meandec": 14.518140060714286, "sigmara": 0.00002779055833156675,
        "sigmadec": 0.000018786625251952534, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.702, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF23aapogvn", "ndethist": "187", "ncovhist": 3403, "mjdstarthist": 60120.25,
        "mjdendhist": 60182.25, "corrected": False, "stellar": False, "ndet": 40,
        "g_r_max": -0.165329, "g_r_max_corr": None, "g_r_mean": 0.08202565, "g_r_mean_corr": None,
        "firstmjd": 60120.35121530015, "lastmjd": 60182.284016199876, "deltajd": 61.93280089972541,
        "meanra": 242.8951132325, "meandec": 58.96757178750001, "sigmara": 0.00005162935652456283,
        "sigmadec": 0.00003591341573141273, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.702, "step_id_corr": "1.2.0"
    },
    {
        "oid": "ZTF22abhuvug", "ndethist": "36", "ncovhist": 709, "mjdstarthist": 59843.5,
        "mjdendhist": 59889.5, "corrected": False, "stellar": False, "ndet": 32,
        "g_r_max": -0.006151, "g_r_max_corr": None, "g_r_mean": 0.06984939, "g_r_mean_corr": None,
        "firstmjd": 59843.44075229997, "lastmjd": 59889.37671299977, "deltajd": 45.93596069980413,
        "meanra": 63.67726868125, "meandec": -16.592766724999997, "sigmara": 0.00004866479443882095,
        "sigmadec": 0.000044234062192514414, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.702, "step_id_corr": "1.1.6"
    },
    {
        "oid": "ZTF19aclljyq", "ndethist": "18", "ncovhist": 463, "mjdstarthist": 58788.19469910022,
        "mjdendhist": 58831.103761599865, "corrected": False, "stellar": False, "ndet": 18,
        "g_r_max": -0.18238258, "g_r_max_corr": None, "g_r_mean": -0.19932938, "g_r_mean_corr": None,
        "firstmjd": 58788.19469910022, "lastmjd": 58831.103761599865, "deltajd": 42.9090624996461,
        "meanra": 26.18924588888889, "meandec": 7.16469718888889, "sigmara": 0.00003226266990285693,
        "sigmadec": 0.00005058473251290063, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.7, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF19abahvdh", "ndethist": "27", "ncovhist": 135, "mjdstarthist": 58652.172268500086,
        "mjdendhist": 58705.165648099966, "corrected": False, "stellar": False, "ndet": 25,
        "g_r_max": -0.20515442, "g_r_max_corr": None, "g_r_mean": -0.13072586, "g_r_mean_corr": None,
        "firstmjd": 58652.172268500086, "lastmjd": 58705.165648099966, "deltajd": 52.99337959988043,
        "meanra": 232.86438422799998, "meandec": 7.09523824, "sigmara": 0.00002413953396673454,
        "sigmadec": 0.00002961887067396273, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.698, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF21abrmefg", "ndethist": "35", "ncovhist": 1718, "mjdstarthist": 59434.367662000004,
        "mjdendhist": 59472.39018520014, "corrected": False, "stellar": False, "ndet": 27,
        "g_r_max": 0.03559, "g_r_max_corr": None, "g_r_mean": 0.41469795, "g_r_mean_corr": None,
        "firstmjd": 59434.367662000004, "lastmjd": 59472.39018520014, "deltajd": 38.0225232001394,
        "meanra": 8.637614792592592, "meandec": 37.13363941851852, "sigmara": 0.00002581825421502012,
        "sigmadec": 0.000018229330487368494, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.696, "step_id_corr": "correction_1.0.6"
    },
    {
        "oid": "ZTF21abaaipx", "ndethist": "40", "ncovhist": 610, "mjdstarthist": 59339.4280208,
        "mjdendhist": 59381.399455999956, "corrected": False, "stellar": False, "ndet": 28,
        "g_r_max": -0.029867, "g_r_max_corr": None, "g_r_mean": 0.24734257, "g_r_mean_corr": None,
        "firstmjd": 59339.4280208, "lastmjd": 59381.399455999956, "deltajd": 41.97143519995734,
        "meanra": 317.3179852928571, "meandec": 5.826158285714286, "sigmara": 0.000025318371727030224,
        "sigmadec": 0.00002492368670016471, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.696, "step_id_corr": "correction_0.0.1"
    },
    {
        "oid": "ZTF20acgznau", "ndethist": "70", "ncovhist": 542, "mjdstarthist": 59126.255636599846,
        "mjdendhist": 59169.147638900205, "corrected": False, "stellar": False, "ndet": 24,
        "g_r_max": -0.0015163422, "g_r_max_corr": None, "g_r_mean": 0.13594627, "g_r_mean_corr": None,
        "firstmjd": 59129.22285880009, "lastmjd": 59169.147638900205, "deltajd": 39.92478010011837,
        "meanra": 343.29855604583327, "meandec": 11.113533154166667, "sigmara": 0.00005033584580645596,
        "sigmadec": 0.000039387307370333566, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.696, "step_id_corr": "corr_bulk_0.0.1"
    },
    {
        "oid": "ZTF22aboisvs", "ndethist": "29", "ncovhist": 1185, "mjdstarthist": 59872.5,
        "mjdendhist": 59930.5, "corrected": False, "stellar": False, "ndet": 24,
        "g_r_max": -0.121521, "g_r_max_corr": None, "g_r_mean": 0.030941969, "g_r_mean_corr": None,
        "firstmjd": 59872.46498840023, "lastmjd": 59930.390219899826, "deltajd": 57.92523149959743,
        "meanra": 132.11901203333335, "meandec": 1.3972640416666664, "sigmara": 0.00003115525870490711,
        "sigmadec": 0.000022454822599413898, "class": "SNIa", "classifier": "lc_classifier",
        "probability": 0.696, "step_id_corr": "1.1.6"
    }
]
