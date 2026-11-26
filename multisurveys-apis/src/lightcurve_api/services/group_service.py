"""Object groups in the light curve: which objects are the same source as this one, and their photometry.

A group is a set of objects, possibly from different surveys, linked by pairs that score at least the method's
threshold (0.95). The light curve lists the group's members and a few nearby objects whose pairs scored below
the threshold, all off until the user turns them on. Their photometry is fetched separately, on demand
(see ``get_group_photometry``), so the object's own light curve never waits for it.

Every object here is named by its survey and that survey's id, as users name it: the ZTF name or the LSST
numeric id, as a string. ``group_id`` is internal and only shown for reference.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Iterable

from core.idmapper.idmapper import parse_oid, public_oid
from core.idmapper.survey_mapper import get_survey_id, get_survey_name
from core.periodogram.barycentric import bjd_tdb_times
from core.repository.queries import association as association_repository
from core.repository.queries.association import SessionFactory
from lightcurve_api.services import lightcurve_service
from lightcurve_api.services.lightcurve_plot_service.service import (
    detection_plot_record,
    forced_photometry_plot_record,
)

DEFAULT_THRESHOLD = 0.95
NEARBY_LIMIT = 5
MAX_OBJECTS_PER_REQUEST = 20
SUPPORTED_SURVEYS = ("ztf", "lsst")
SUPPORTED_SIDS = tuple(get_survey_id(survey) for survey in SUPPORTED_SURVEYS)
MJD_EPOCH = datetime(1858, 11, 17)


@dataclass
class GroupObject:
    oid: str  # the survey's own id: ZTF name or LSST numeric id
    survey_id: str  # "ztf" or "lsst"
    is_self: bool = False
    in_group: bool = True
    dist: float | None = None  # arcseconds, of the pair shown in `score`
    score: float | None = None
    linked_via: str | None = None  # the other end of that pair, when it isn't the object being viewed
    n_det: int | None = None  # None: the object isn't in the object table
    firstmjd: float | None = None
    lastmjd: float | None = None

    @property
    def key(self) -> str:
        return f"{self.survey_id}:{self.oid}"


@dataclass
class GroupInfo:
    group_id: int | None  # None: the object has no group
    group_version: int | None
    method_version: int
    threshold: float
    members: list[GroupObject] = field(default_factory=list)  # the object being viewed comes first
    nearby: list[GroupObject] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["members"] = [{**asdict(m), "key": m.key} for m in self.members]
        data["nearby"] = [{**asdict(n), "key": n.key} for n in self.nearby]
        return data


def mjd_to_date(mjd: float | None) -> str:
    """An MJD as an ISO date (2018-11-02), or "" for None."""
    return "" if mjd is None else (MJD_EPOCH + timedelta(days=mjd)).date().isoformat()


def _public_oid(key: tuple[int, int]) -> str:
    oid, sid = key
    return public_oid(get_survey_name(sid), oid)


def get_group_info(oid: str, survey_id: str, session_factory: SessionFactory) -> GroupInfo | None:
    """The object's group and nearby objects, in one statement, or None when there is no association data."""
    self_key = (parse_oid(survey_id, oid), get_survey_id(survey_id))
    rows = association_repository.get_group_neighbourhood(session_factory, *self_key)
    if not rows:
        return None
    first = rows[0]
    return build_group_info(
        self_key=self_key,
        members=[(row.oid, row.sid) for row in rows if row.is_member],
        pairs=[row for row in rows if row.oid_b is not None],
        threshold=(first.params or {}).get("groups", {}).get("threshold", DEFAULT_THRESHOLD),
        method_version=first.method_version,
        group_id=first.group_id,
        group_version=first.group_version,
        stats={(row.oid, row.sid): row for row in rows},
    )


def build_group_info(
    self_key: tuple[int, int],
    members: Iterable[tuple[int, int]],
    pairs: Iterable,
    threshold: float,
    method_version: int,
    group_id: int | None = None,
    group_version: int | None = None,
    nearby_limit: int = NEARBY_LIMIT,
    stats: dict | None = None,
) -> GroupInfo:
    """Describe each member by its pair with the viewed object, and pick the strongest nearby non-members.

    ``pairs`` are rows with oid_a, sid_a, oid_b, sid_b, dist and score, each touching at least one member.
    A member that isn't paired with the viewed object directly (it joined through another member) is
    described by its strongest pair inside the group. A nearby object is described by its strongest pair
    with any member. ``stats`` maps (oid, sid) to a row with n_det, firstmjd and lastmjd.
    """
    stats = stats or {}
    member_set = set(members) | {self_key}
    direct: dict = {}  # member -> pair with the viewed object
    best_inside: dict = {}  # member -> (pair, the other member)
    best_nearby: dict = {}  # non-member -> (pair, the member it pairs with)

    for pair in pairs:
        a, b = (pair.oid_a, pair.sid_a), (pair.oid_b, pair.sid_b)
        a_in, b_in = a in member_set, b in member_set
        if a_in and b_in:
            if self_key in (a, b):
                direct[b if a == self_key else a] = pair
            for this, other in ((a, b), (b, a)):
                if this not in best_inside or pair.score > best_inside[this][0].score:
                    best_inside[this] = (pair, other)
        elif a_in or b_in:
            member, outsider = (a, b) if a_in else (b, a)
            if outsider[1] not in SUPPORTED_SIDS:
                continue
            if outsider not in best_nearby or pair.score > best_nearby[outsider][0].score:
                best_nearby[outsider] = (pair, member)

    def describe(key, in_group, is_self=False, pair=None, via=None):
        obj = GroupObject(
            oid=_public_oid(key),
            survey_id=get_survey_name(key[1]),
            is_self=is_self,
            in_group=in_group,
            dist=float(pair.dist) if pair is not None else None,
            score=float(pair.score) if pair is not None else None,
            linked_via=_public_oid(via) if via not in (None, self_key) else None,
        )
        row = stats.get(key)
        if row is not None:
            obj.n_det, obj.firstmjd, obj.lastmjd = row.n_det, row.firstmjd, row.lastmjd
        return obj

    others = []
    for key in member_set - {self_key}:
        if key[1] not in SUPPORTED_SIDS:
            continue
        if key in direct:
            pair, via = direct[key], self_key
        else:
            pair, via = best_inside.get(key, (None, None))
        others.append(describe(key, in_group=True, pair=pair, via=via))
    others.sort(key=lambda m: (m.linked_via is not None, -(m.score or 0), m.dist or 0))

    nearby = [describe(key, in_group=False, pair=pair, via=via) for key, (pair, via) in best_nearby.items()]
    nearby.sort(key=lambda n: (-(n.score or 0), n.dist or 0))

    return GroupInfo(
        group_id=group_id,
        group_version=group_version,
        method_version=method_version,
        threshold=threshold,
        members=[describe(self_key, in_group=True, is_self=True), *others],
        nearby=nearby[:nearby_limit],
    )


def parse_object_keys(objects: str) -> dict[str, list[int]]:
    """Parse ``ztf:ZTF19aaxlmra,lsst:313853798223069211`` into the stored oids of each survey."""
    keys = [k.strip() for k in objects.split(",") if k.strip()]
    if len(keys) > MAX_OBJECTS_PER_REQUEST:
        raise ValueError(f"Too many objects: {len(keys)}, at most {MAX_OBJECTS_PER_REQUEST} per request.")
    by_survey: dict[str, list[int]] = {}
    for key in keys:
        survey, sep, oid = key.partition(":")
        survey = survey.lower()
        if not sep or survey not in SUPPORTED_SURVEYS:
            raise ValueError(f"Invalid object '{key}': expected <survey>:<oid>, with survey ztf or lsst.")
        by_survey.setdefault(survey, []).append(parse_oid(survey, oid))  # ValueError for an invalid id
    return by_survey


def load_photometry(
    objects: str, session_factory: SessionFactory, exclude: tuple[str, int] | None = None
) -> tuple[list, list]:
    """Detections and forced photometry of several objects (``objects`` as in parse_object_keys): two statements
    per survey. ``exclude``, a (survey, stored oid) pair, leaves out the object being viewed, whose photometry the
    caller already has."""
    detections, forced = [], []
    for survey, oids in parse_object_keys(objects).items():
        oids = [oid for oid in oids if (survey, oid) != exclude]
        if oids:
            detections += lightcurve_service.get_detections_by_list(oids, survey, session_factory)
            forced += lightcurve_service.get_forced_photometry_by_list(oids, survey, session_factory)
    return detections, forced


def get_group_photometry(
    objects: str, session_factory: SessionFactory, ra: float | None = None, dec: float | None = None
) -> dict:
    """Detections and forced photometry of several objects, as plot records tagged with their object.

    Non-detections are left out: limiting magnitudes of other objects would crowd the difference view, and the
    light curve only draws those of the object being viewed. Each record has its ``bjd_tdb``, from the sky position
    ``ra``/``dec`` (the viewed object's), else the mean of all these detections.
    """
    detections, forced = load_photometry(objects, session_factory)
    det_times, fp_times = bjd_tdb_times(detections, forced, ra, dec)
    return {
        "detections": [
            {**detection_plot_record(det, t), "oid": public_oid(det.survey_id, det.oid)}
            for det, t in zip(detections, det_times)
        ],
        "forced_photometry": [
            {**forced_photometry_plot_record(fp, t), "oid": public_oid(fp.survey_id, fp.oid)}
            for fp, t in zip(forced, fp_times)
        ],
    }
