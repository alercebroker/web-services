"""Object groups in the light curve: which objects are the same source as this one, and their photometry.

A group is a set of objects, possibly from different surveys, linked by pairs that score at least the method's
threshold (0.95). The light curve lists the group's members and a few nearby objects whose pairs scored below
the threshold, all off until the user turns them on. Their photometry is fetched separately, on demand
(see ``get_group_photometry``), so the object's own light curve never waits for it.

Every object here is named by its survey and that survey's id, as users name it: the ZTF name or the LSST
numeric id, as a string. ``group_id`` is internal and only shown for reference.
"""

import logging
import os
from datetime import datetime, timedelta
from dataclasses import asdict, dataclass, field
from typing import Callable, ContextManager, Iterable

from sqlalchemy.orm import Session

from core.idmapper.idmapper import decode_masterid, parse_oid
from core.idmapper.survey_mapper import get_survey_id, get_survey_name
from core.repository.queries import association as association_repository
from lightcurve_api.services import lightcurve_service
from lightcurve_api.services.lightcurve_plot_service.service import (
    detection_plot_record,
    forced_photometry_plot_record,
)

logger = logging.getLogger(__name__)

SessionFactory = Callable[..., ContextManager[Session]]

DEFAULT_THRESHOLD = 0.95
NEARBY_LIMIT = 5
MAX_OBJECTS_PER_REQUEST = 20
SUPPORTED_SIDS = (get_survey_id("ztf"), get_survey_id("lsst"))
MJD_EPOCH = datetime(1858, 11, 17)


def association_enabled() -> bool:
    """Groups are shown only where ASSOCIATION_SCHEMA is set (local demo); production doesn't have the tables yet."""
    return bool(os.getenv("ASSOCIATION_SCHEMA"))


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


def display_oid(oid: int, sid: int) -> str:
    """The id users know an object by: the ZTF name, or the numeric id of other surveys."""
    if sid == get_survey_id("ztf"):
        return decode_masterid(oid)[1]
    return str(oid)


def get_group_info(oid: str, survey_id: str, session_factory: SessionFactory) -> GroupInfo | None:
    """The object's group and nearby objects, or None when there is no association data at all."""
    master_id = parse_oid(survey_id, oid)
    sid = get_survey_id(survey_id)

    group = association_repository.get_object_group(session_factory, master_id, sid)
    if group is not None:
        method = association_repository.get_method(session_factory, group.method_version)
        members = association_repository.get_group_members(session_factory, group.group_id)
    else:
        method = association_repository.get_method(session_factory)
        members = [(master_id, sid)]
    if method is None:
        return None

    threshold = (method.params or {}).get("groups", {}).get("threshold", DEFAULT_THRESHOLD)
    pairs = association_repository.get_pairs_touching(session_factory, members, method.method_version)
    objects = set(members) | {(master_id, sid)}
    for pair in pairs:
        objects |= {(pair.oid_a, pair.sid_a), (pair.oid_b, pair.sid_b)}
    stats = association_repository.get_object_stats(session_factory, objects)
    return build_group_info(
        self_key=(master_id, sid),
        members=members,
        pairs=pairs,
        threshold=threshold,
        method_version=method.method_version,
        group_id=group.group_id if group else None,
        group_version=group.group_version if group else None,
        stats=stats,
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

    def with_stats(obj, key):
        row = stats.get(key)
        if row is not None:
            obj.n_det, obj.firstmjd, obj.lastmjd = row.n_det, row.firstmjd, row.lastmjd
        return obj

    def describe(key, pair, via, in_group):
        obj = GroupObject(
            oid=display_oid(*key),
            survey_id=get_survey_name(key[1]),
            in_group=in_group,
            dist=float(pair.dist) if pair is not None else None,
            score=float(pair.score) if pair is not None else None,
            linked_via=display_oid(*via) if via is not None and via != self_key else None,
        )
        return with_stats(obj, key)

    others = []
    for key in member_set - {self_key}:
        if key[1] not in SUPPORTED_SIDS:
            continue
        if key in direct:
            others.append(describe(key, direct[key], self_key, True))
        elif key in best_inside:
            others.append(describe(key, *best_inside[key], True))
        else:
            others.append(describe(key, None, None, True))
    others.sort(key=lambda m: (m.linked_via is not None, -(m.score or 0), m.dist or 0))

    me = with_stats(GroupObject(oid=display_oid(*self_key), survey_id=get_survey_name(self_key[1]), is_self=True), self_key)

    nearby = [describe(key, pair, via, False) for key, (pair, via) in best_nearby.items()]
    nearby.sort(key=lambda n: (-(n.score or 0), n.dist or 0))

    return GroupInfo(
        group_id=group_id,
        group_version=group_version,
        method_version=method_version,
        threshold=threshold,
        members=[me, *others],
        nearby=nearby[:nearby_limit],
    )


def parse_object_keys(objects: str) -> dict[str, list[str]]:
    """Parse ``ztf:ZTF19aaxlmra,lsst:313853798223069211`` into oids per survey, validating each one."""
    keys = [k.strip() for k in objects.split(",") if k.strip()]
    if len(keys) > MAX_OBJECTS_PER_REQUEST:
        raise ValueError(f"Too many objects: {len(keys)}, at most {MAX_OBJECTS_PER_REQUEST} per request.")
    by_survey: dict[str, list[str]] = {}
    for key in keys:
        survey, sep, oid = key.partition(":")
        survey = survey.lower()
        if not sep or survey not in ("ztf", "lsst"):
            raise ValueError(f"Invalid object '{key}': expected <survey>:<oid>, with survey ztf or lsst.")
        parse_oid(survey, oid)  # raises ValueError for an invalid id
        by_survey.setdefault(survey, []).append(oid)
    return by_survey


def get_group_photometry(objects: str, session_factory: SessionFactory) -> dict:
    """Detections and forced photometry of several objects, as plot records tagged with their object.

    Non-detections are left out: limiting magnitudes of other objects would crowd the difference view, and the
    light curve only draws those of the object being viewed.
    """
    detections, forced = [], []
    for survey, oids in parse_object_keys(objects).items():
        sid = get_survey_id(survey)
        seen = set()
        for det in lightcurve_service.get_detections_by_list(oids, survey, session_factory):
            key = (det.oid, getattr(det, "measurement_id", None))
            if key in seen:
                continue
            seen.add(key)
            detections.append({**detection_plot_record(det), "oid": display_oid(det.oid, sid)})
        for fp in lightcurve_service.get_forced_photometry_by_list(oids, survey, session_factory):
            forced.append({**forced_photometry_plot_record(fp), "oid": display_oid(fp.oid, sid)})
    return {"detections": detections, "forced_photometry": forced}
