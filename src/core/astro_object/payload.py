import math

from shared.utils.queries import Payload, FilterRules


class AstroObjectPayload(Payload):
    class AstroObjectHelpers(Payload.Helpers):
        @staticmethod
        def query_for_locs(ra, dec, radius):
            return {
                '$centerSphere': [[ra - 180, dec], math.radians(radius / 3600)]
            }

    filter_rules = {
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
    paginate_map = {
        'page': 'page',
        'per_page': 'page_size',
        'count': 'count'
    }
    sort_map = {
        'key': 'order_by',
        'direction': 'order_mode'
    }
    direction_map = {
        'ASC': 1,
        'DESC': -1
    }
