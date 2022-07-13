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


class SortMap(TypedDict):
    key: str
    direction: str


class Payload(abc.ABC):
    """Base class for mongo query generation.

    Subclasses must define the `filter_rules` dictionary, mapping fields
    in the database to `FilterRules`. The dictionaries `paginate_map`,
    `sort_map` and `direction_map` are optional. If one of the latter two
    are defined, the other must be defined as well.

    Parameters
    ----------
    filter_args : dict
        Input arguments for filtering (usually parsed from `get` methods)
    paginate_args : dict, None
        Input arguments for pagination (usually parsed from `get` methods)
    sort_args : dict, None
        Input arguments for sorting (usually parsed from `get` methods)

    Attributes
    ----------
    filter_rules: dict[str, FilterRules]
        Mapping from field name to rules, e.g.,
        `{'a': FilterRules(['b'], '$gt', float)}`
    raw_filter : dict
        Input arguments for filtering, e.g., `{'b': '10'}`
    filter : dict
        Query ready dictionary, e.g., `{'a': {'$gt': 10.0}}`
    paginate_map : PaginateMap
        Mapping from pagination arguments to corresponding parser keys, e.g.,
        `{'page': 'page', 'per_page': 'page_size'}`
    raw_paginate : dict, None
        Input arguments for pagination, e.g., `{'page_size': 2}`
    paginate : dict
        Pagination parameters, e.g., `{'per_page': 2}`
    sort_map : SortMap
        Mapping from sorting arguments to corresponding parser keys, e.g.,
        `{'key': 'order_by', 'direction': 'order_mode'}`
    direction_map : dict[str, int]
        Mapping from direction values to either 1 (ascending) or -1
        (descending), e.g., `{'ASC': 1, 'DESC': -1}`
    raw_sort : dict, None
        Input arguments for sorting, e.g., `{'key': 'a', 'direction': 'ASC'}`
    sort : list[tuple], None
        Value for sorting, e.g., `[('a', 1)]`
    """
    filter_rules: Dict[str, FilterRules]
    paginate_map: PaginateMap
    sort_map: SortMap
    direction_map: Dict[str, int]  # Values are 1 (asc) and -1 (desc)

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

    def __init__(self, filter_args, paginate_args=None, sort_args=None):
        self.raw_filter = filter_args
        self.raw_paginate = paginate_args if paginate_args else {}
        self.raw_sort = sort_args if sort_args else {}

    @property
    def filter(self):
        return {
            key: self._generate_filter_value(key)
            for key in self.filter_rules if not self._is_null(key)
        }

    @property
    def paginate(self):
        return {
            key: self.raw_paginate[value]
            for key, value in self.paginate_map.items()
            if self.raw_paginate.get(value) is not None
        }

    @property
    def sort(self):
        try:
            keys = self.raw_sort.get(self.sort_map['key'])
            directions = self.raw_sort.get(self.sort_map['direction'])
        except AttributeError:
            return None
        return [
            (key, self.direction_map[direction])
            for key, direction in zip(self.Helpers.list_of_str(keys),
                                      self.Helpers.list_of_str(directions))
        ] if None not in [keys, directions] else None

    def _generate_filter_value(self, key):
        rule = self.filter_rules[key]
        value = rule.process(*[self.raw_filter[key] for key in rule.raw_key])
        if rule.query_key is None:
            return value
        elif isinstance(rule.query_key, str):
            return {rule.query_key: value}
        return {qkey: val for qkey, val in zip(rule.query_key, value)}

    def _is_null(self, key):
        """Checks if any of the raw keys for filter is missing from input.

        It considers them missing if they have a value of `None` or if the
        raw key itself is not present in the arguments.

        Parameters
        ----------
        key : str
            Filter key to check for required input keys

        Returns
        -------
        bool
            Whether any of the required input keys is missing
        """
        rule = self.filter_rules[key]
        return any(self.raw_filter.get(rkey) is None for rkey in rule.raw_key)
