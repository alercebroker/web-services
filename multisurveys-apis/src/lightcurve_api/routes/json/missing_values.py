"""ZTF points without a corrected magnitude answer null in the JSON, not 0, and ZTF rows carry the ZTF name
as oid, not the internal numeric id.

The models turn the NULL ``*_corr`` columns into 0 (``set_defaults``), and the lightcurve plot relies on that
0 to tell corrected points from uncorrected ones. So the 0 stays inside the models and becomes null only here,
when the JSON answer is built. A real magnitude or error is never exactly 0, so 0 only ever means "missing".
"""

from fastapi.encoders import jsonable_encoder

from core.idmapper.idmapper import decode_ids

CORRECTED_FIELDS = ("magpsf_corr", "sigmapsf_corr", "sigmapsf_corr_ext", "mag_corr", "e_mag_corr", "e_mag_corr_ext")


def json_rows(rows) -> list[dict]:
    items = []
    for row in rows:
        item = jsonable_encoder(row)
        if item.get("survey_id") == "ztf":
            for field in CORRECTED_FIELDS:
                if item.get(field) == 0:
                    item[field] = None
            decode_ids([item])
        items.append(item)
    return items
