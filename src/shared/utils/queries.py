import math
from abc import ABC
from dataclasses import dataclass
from typing import Union, Callable, Dict, Sequence


def _loc_query(ra, dec, radius):
    return {'$centerSphere': [[ra, dec], math.radians(radius / 3600)]}


@dataclass
class QueryRules:
    raw_key: Sequence[str]  # Key(s) from raw dict that are arguments for process
    query_key: Union[str, Sequence, None]  # Key(s) that represent the mongo query
    process: Callable


class QueryFactory(ABC):
    _rules: Dict[str, QueryRules]

    def __init__(self, parsed_dict):
        self.raw_query = parsed_dict

    @property
    def clean_query(self):
        return {
            key: self._generate_value(key)
            for key in self._rules if not self._is_null(key)
        }

    def _generate_value(self, key):
        rule = self._rules[key]
        value = rule.process(*[self.raw_query[key] for key in rule.raw_key])
        if rule.query_key is None:
            return value
        elif isinstance(rule.query_key, str):
            return {rule.query_key: value}
        # Assumes query_key is a sequence
        return {qkey: val for qkey, val in zip(rule.query_key, value)}

    def _is_null(self, key):
        rule = self._rules[key]
        return any(self.raw_query[rkey] is None for rkey in rule.raw_key)


class ObjectQueryFactory(QueryFactory):
    _rules = {
        'oid': QueryRules(['oid'], '$in', list),
        'firstmjd': QueryRules(['firstmjd'], '$gte', float),
        'lastmjd': QueryRules(['lastmjd'], '$lte', float),
        'ndet': QueryRules(['ndet'], ['$gte', '$lte'], list),
        'loc': QueryRules(['ra', 'dec', 'radius'], '$geoWithin', _loc_query)
    }
