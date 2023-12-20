required_detection_fields = {
    "candid",
    "tid",
    "oid",
    "mjd",
    "fid",
    "ra",
    "dec",
    "mag",
    "e_mag",
    "isdiffpos",
    "corrected",
    "dubious",
    "has_stamp",
}

required_forced_photometry_fields = {
    "tid",
    "oid",
    "pid",
    "mjd",
    "fid",
    "ra",
    "dec",
    "mag",
    "e_mag",
    "isdiffpos",
    "corrected",
    "dubious",
    "has_stamp",
}

required_non_detection_fields = {
    "aid",
    "tid",
    "sid",
    "oid",
    "mjd",
    "fid",
    "diffmaglim",
}


def create_object_data_mongo(oid, aid):
    return {
        "_id": aid,
        "oid": oid,
    }


def create_object_data_psql(oid):
    return {
        "oid": oid,
        "ndethist": 0,
        "ncovhist": 0,
        "meanra": 0,
        "meandec": 0,
        "deltajd": 0,
        "firstmjd": 0,
        "lastmjd": 0,
        "step_id_corr": 0,
    }


def create_detection_data_mongo(oid, candid, aid, tid):
    return {
        "_id": candid,
        "aid": aid,
        "oid": oid,
        "tid": tid,
        "mjd": 59000,
        "fid": 1,
        "ra": 10,
        "dec": 20,
        "mag": 15,
        "e_mag": 0.5,
        "isdiffpos": 1,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
    }


def create_detection_data_psql(oid, candid):
    return {
        "candid": candid,
        "oid": oid,
        "mjd": 59000,
        "fid": 1,
        "pid": 1,
        "isdiffpos": 1,
        "ra": 10,
        "dec": 20,
        "magpsf": 15,
        "sigmapsf": 0.5,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
        "step_id_corr": "test",
    }


def create_forced_photometry_data_psql(oid, pid):
    return {
        "oid": oid,
        "mjd": 59000,
        "fid": 1,
        "pid": pid,
        "isdiffpos": 1,
        "ra": 10,
        "dec": 20,
        "mag": 15,
        "e_mag": 0.5,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
    }


def create_forced_photometry_data_mongo(oid, pid, aid, tid):
    return {
        "_id": f"{oid}_{pid}",
        "aid": aid,
        "oid": oid,
        "pid": pid,
        "tid": tid,
        "mjd": 59000,
        "fid": "r",
        "ra": 10,
        "dec": 20,
        "mag": 15,
        "e_mag": 0.5,
        "isdiffpos": 1,
        "corrected": False,
        "dubious": False,
        "has_stamp": False,
    }


def create_non_detection_data_psql(oid):
    return {"oid": oid, "fid": 1, "mjd": 59000, "diffmaglim": 100}


def create_non_detection_data_mongo(oid, aid, tid):
    return {
        "tid": tid,
        "aid": aid,
        "oid": oid,
        "mjd": 59000,
        "fid": 1,
        "diffmaglim": 0.5,
    }
