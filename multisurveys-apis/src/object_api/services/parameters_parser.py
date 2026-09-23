from core.idmapper.idmapper import encode_ids


def search_order_state(oids: list, order_by: str) -> str:
    if oids is None and order_by is None:
        order_by = "probability"

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


def parse_oids_to_int(oids: list, survey: str) -> list:
    if oids is not None:
        encode_oids = encode_ids(survey, oids)
        oids = [int(object) for object in encode_oids]

    return oids
