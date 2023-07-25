from typing import List
from astroobject.core.domain.astroobject_model import AstroObject
from astroobject.core.domain.astroobject_queries import GetAstroObjectsQuery
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..domain.astroobject_repository import AstroObjectRepository


class AstroObjectSQLRespository(AstroObjectRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _parse_objects_query(self, query: GetAstroObjectsQuery):
        pass

    def _parse_conesearch(self, conesearch: dict):
        try:
            ra, dec, radius = conesearch["ra"], conesearch["dec"], conesearch["radius"]
        except KeyError:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
        else:
            return True

    def _parse_filters(self, filters: dict):  # ?
        pass

    def get_objects(self, query: GetAstroObjectsQuery) -> List[AstroObject]:
        return super().get_objects(query)
