from core.idmapper.idmapper import encode_ids


def search_order_state(oids: list, order_by: str, classifier: str | None = None) -> str:
    # Without classification filters the newest alerts come first: sorting by probability there is slow, and
    # mixes the predictions of every classifier.
    if oids is None and order_by is None:
        order_by = "probability" if classifier is not None else "lastmjd"

    # Without a classifier filter each row shows one classifier's prediction, or none: probability is not sortable.
    if classifier is None and order_by == "probability":
        order_by = "lastmjd"

    if oids is not None and order_by == "oid_list":
        order_by = None

    return order_by


def ndet_build(n_det_min: int, n_det_max: int) -> list:
    n_det = []
    if n_det_min is not None:
        n_det.append(n_det_min)
    if n_det_max is not None:
        n_det.append(n_det_max)
    n_det = n_det if len(n_det) > 0 else None

    return n_det


def mjd_range_build(mjd_min: float, mjd_max: float) -> list:
    # object_filters reads [min] as mjd >= min and [min, max] as a range (for firstmjd and lastmjd),
    # so "max only" needs a lower bound: 0 is before any MJD.
    if mjd_max is not None:
        return [mjd_min if mjd_min is not None else 0, mjd_max]
    if mjd_min is not None:
        return [mjd_min]

    return None


def parse_oids_to_int(oids: list, survey: str) -> list:
    if oids is not None:
        encode_oids = encode_ids(survey, oids)
        oids = [int(object) for object in encode_oids]

    return oids
