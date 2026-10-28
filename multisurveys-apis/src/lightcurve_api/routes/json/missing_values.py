"""ZTF magnitudes that are missing or couldn't be computed answer null in the JSON, and ZTF rows carry the ZTF
name as oid, not the internal numeric id.

The models turn the NULL ``*_corr`` columns into 0 (``set_defaults``), and the lightcurve plot relies on that
0 to tell corrected points from uncorrected ones. So the 0 stays inside the models and becomes null only here,
when the JSON answer is built. A real magnitude or error is never exactly 0, so 0 only ever means "missing".
The pipeline writes 100 (``NOT_COMPUTED_MAG``) where a value can't be computed, which also becomes null.
NaN and infinite floats, in any survey, become null too: JSON can't carry them.
"""

import math

from fastapi.encoders import jsonable_encoder

from core.idmapper.idmapper import decode_ids
from lightcurve_api.models.lightcurve_item import NOT_COMPUTED_MAG

CORRECTED_FIELDS = ("magpsf_corr", "sigmapsf_corr", "sigmapsf_corr_ext", "mag_corr", "e_mag_corr", "e_mag_corr_ext")
FORCED_PHOTOMETRY_FIELDS = ("mag", "e_mag")


def json_rows(rows) -> list[dict]:
    items = []
    for row in rows:
        item = jsonable_encoder(row)
        for field, value in item.items():
            if isinstance(value, float) and not math.isfinite(value):
                item[field] = None
        if item.get("survey_id") == "ztf":
            for field in CORRECTED_FIELDS:
                if item.get(field) in (0, NOT_COMPUTED_MAG):
                    item[field] = None
            for field in FORCED_PHOTOMETRY_FIELDS:
                if item.get(field) == NOT_COMPUTED_MAG:
                    item[field] = None
            decode_ids([item])
        items.append(item)
    return items
