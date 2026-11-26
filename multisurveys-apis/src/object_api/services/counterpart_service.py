"""The "Also seen as" column of the results table: the other members of each listed object's association group.

Like the light curve's group panel, it shows only where ASSOCIATION_SCHEMA is set, and the route treats a failed
lookup as no counterparts, so the results are shown either way. A page costs one statement whatever its size:
each query is a full round trip to a distant database (see "The database is far from the APIs" in the
repository's CLAUDE.md).
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from core.idmapper.idmapper import parse_oid, public_oid
from core.idmapper.survey_mapper import get_survey_id, get_survey_name
from core.repository.queries import association as association_repository

MAX_LISTED_PER_SURVEY = 10  # links shown in a chip's list; the chip still counts them all


@dataclass
class Counterpart:
    oid: str  # the survey's own id: ZTF name or LSST numeric id
    survey_id: str
    dist: float | None = None  # arcseconds, of the direct pair with the listed object
    score: float | None = None  # None: the member joined the group through another member
    n_det: int | None = None

    @property
    def description(self) -> str:
        parts = [self.oid]
        if self.score is not None:
            parts.append(f'{self.dist:.2f}", score {self.score:.2f}')
        else:
            parts.append("linked through another member")
        if self.n_det is not None:
            parts.append(f"{self.n_det} detections")
        return " · ".join(parts)


@dataclass
class SurveyCounterparts:
    survey_id: str
    count: int
    members: list[Counterpart] = field(default_factory=list)  # strongest first, at most MAX_LISTED_PER_SURVEY

    @property
    def label(self) -> str:
        return self.survey_id.upper()

    @property
    def title(self) -> str:
        """The tooltip of the chip: the members it lists, one per line."""
        lines = [f"Same source in {self.label} (association score ≥ threshold):"]
        lines += [f"  {member.description}" for member in self.members]
        if self.count > len(self.members):
            lines.append(f"  … and {self.count - len(self.members)} more")
        return "\n".join(lines)


def get_counterparts(session_factory, survey: str, oids: Iterable[str]) -> dict[str, list[SurveyCounterparts]]:
    """The other members of each listed object's group, by survey, keyed by the oid as the table shows it.

    Objects without a group, or alone in it, are left out.
    """
    sid = get_survey_id(survey)
    listed = {(parse_oid(survey, oid), sid): str(oid) for oid in oids}

    rows_by_listed = defaultdict(list)
    for row in association_repository.get_counterpart_rows(session_factory, listed):
        rows_by_listed[(row.listed_oid, row.listed_sid)].append(row)

    return {listed[key]: build_survey_counterparts(key[1], rows) for key, rows in rows_by_listed.items()}


def build_survey_counterparts(listed_sid: int, rows: list) -> list[SurveyCounterparts]:
    """Group a listed object's fellow members by survey: other surveys first, then duplicates in its own.

    ``rows`` are get_counterpart_rows' rows of that listed object.
    """
    by_sid = defaultdict(list)
    for row in rows:
        by_sid[row.sid].append(
            Counterpart(
                oid=public_oid(get_survey_name(row.sid), row.oid),
                survey_id=get_survey_name(row.sid),
                dist=row.dist,
                score=row.score,
                n_det=row.n_det,
            )
        )

    result = []
    for m_sid in sorted(by_sid, key=lambda s: (s == listed_sid, s)):
        found = by_sid[m_sid]
        found.sort(key=lambda c: (c.score is None, -(c.score or 0), -(c.n_det or 0)))
        result.append(
            SurveyCounterparts(
                survey_id=get_survey_name(m_sid), count=len(found), members=found[:MAX_LISTED_PER_SURVEY]
            )
        )
    return result
