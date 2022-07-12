import math

from shared.utils.queries import PayloadFactory, FilterRules


class AstroObjectPayload(PayloadFactory):
    class AstroObjectHelpers(PayloadFactory.Helpers):
        @staticmethod
        def query_for_locs(ra, dec, radius):
            return {'$centerSphere': [[ra, dec], math.radians(radius / 3600)]}

    _rules = {
        'oid': FilterRules(
            ['oid'],
            '$in',
            AstroObjectHelpers.list_of_str
        ),
        'firstmjd': FilterRules(
            ['firstmjd'],
            ['$gte', '$lte'],
            AstroObjectHelpers.list_of_float
        ),
        'lastmjd': FilterRules(
            ['lastmjd'],
            ['$gte', '$lte'],
            AstroObjectHelpers.list_of_float
        ),
        'ndet': FilterRules(
            ['ndet'],
            ['$gte', '$lte'],
            AstroObjectHelpers.list_of_int
        ),
        'loc': FilterRules(
            ['ra', 'dec', 'radius'],
            '$geoWithin',
            AstroObjectHelpers.query_for_locs
        )
    }


class AstroObjectService:
    def __init__(self, list_object_repository, single_object_repository):
        self.list_object_repository = list_object_repository
        self.single_object_repository = single_object_repository

    def get_list_object(self, payload: AstroObjectPayload):
        return self.list_object_repository.get(payload)

    def get_single_object(self, payload: AstroObjectPayload):
        return self.single_object_repository.get(payload)
