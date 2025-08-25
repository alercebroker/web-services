from sqlalchemy.orm.session import Session


def conesearch_service(psql_session: Session):
    def conesearch(ra: float, dec: float, radius: float):
        pass

    return conesearch
