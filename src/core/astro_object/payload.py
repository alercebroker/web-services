import math

from shared.utils.queries import PayloadFactory, FilterRules


class AstroObjectPayload(PayloadFactory):
    class AstroObjectHelpers(PayloadFactory.Helpers):
        @staticmethod
        def query_for_locs(ra, dec, radius):
            return {'$centerSphere': [[ra, dec], math.radians(radius / 3600)]}

    _rules = {
        'aid': FilterRules(
            ['aid'],
            '$in',
            AstroObjectHelpers.list_of_str
        ),
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
