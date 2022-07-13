import abc
from dataclasses import dataclass
from typing import Union, Callable, Dict, Sequence, TypedDict


def _ensure_list(arg, argtype):
    if isinstance(arg, argtype):
        return [arg]
    return list(arg)


@dataclass
class FilterRules:
    """
    Rules to transform argument dictionary into a query for mongo.

    If `query_key` is a sequence, the output from `process` should also
    be a sequence. There is no check for mismatching sizes between these
    sequences. This is intentional to allow for ranges that only define a
    lower limit and have open upper bounds.

    If `query_key` is `None`, then it is considered a query for exact match.

    Attributes
    ----------
    raw_key : Sequence
        Key(s) from raw dictionary whose values are used as args for `process`
    query_key : str, Sequence or None
        Key(s) used for mongo queries such as, `$in`, `$gt`, etc.
    process: callable
        Takes `raw_key` values as inputs and outputs value(s) for `query_key`
    """
    raw_key: Sequence[str]  # Key(s) from raw dict that are arguments for process
    query_key: Union[str, Sequence, None]  # Key(s) that represent the mongo query
    process: Callable


class PaginateMap(TypedDict, total=False):
    page: str
    per_page: str
    count: str
    max_results: str


class OrderMap(TypedDict):
    key: str
    direction: str


class Payload(abc.ABC):
    """Base class for mongo query generation.

    Subclasses must define the `_filter_rules` dictionary, mapping fields
    in the database to `QueryRules`.

    Attributes
    ----------
    raw_filter : dict
        Input arguments
    filter_by : dict
        Query ready dictionary
    """
    _filter_rules: Dict[str, FilterRules]
    _paginate_map: PaginateMap
    _order_map: OrderMap
    _direction_map: Dict[str, int]  # Values should be 1 (asc) and -1 (desc)

    class Helpers:
        @staticmethod
        def list_of_str(arg):
            return _ensure_list(arg, str)

        @staticmethod
        def list_of_int(arg):
            return _ensure_list(arg, int)

        @staticmethod
        def list_of_float(arg):
            return _ensure_list(arg, (int, float))

    def __init__(self, filter_args, paginate_args=None, order_args=None):
        """
        Parameters
        ----------
        filter_args : dict
            Input arguments (usually parsed from `get` methods)
        """
        self.raw_filter = filter_args
        self.raw_paginate = paginate_args if paginate_args else {}
        self.raw_sort = order_args if order_args else {}

    @property
    def filter_by(self):
        return {
            key: self._generate_value(key)
            for key in self._filter_rules if not self._is_null(key)
        }

    @property
    def paginate(self):
        return {
            key: self.raw_paginate[key] for key in self._paginate_map
            if self.raw_paginate.get(key) is not None
        }

    @property
    def sort(self):
        try:
            keys = self.raw_sort.get(self._order_map['key'])
            directions = self.raw_sort.get(self._order_map['direction'])
        except AttributeError:
            return None
        return [
            (key, self._direction_map[direction])
            for key, direction in zip(self.Helpers.list_of_str(keys),
                                      self.Helpers.list_of_str(directions))
        ] if None not in [keys, directions] else None

    def _generate_value(self, key):
        rule = self._filter_rules[key]
        value = rule.process(*[self.raw_filter[key] for key in rule.raw_key])
        if rule.query_key is None:
            return value
        elif isinstance(rule.query_key, str):
            return {rule.query_key: value}
        return {qkey: val for qkey, val in zip(rule.query_key, value)}

    @staticmethod
    def _is_key_missing(dictionary, key):
        return dictionary.get(key) is None

    def _is_null(self, key):
        rule = self._filter_rules[key]
        return any(self.raw_filter.get(rkey) is None for rkey in rule.raw_key)
