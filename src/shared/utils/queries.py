import abc
from dataclasses import dataclass
from typing import Union, Callable, Dict, Sequence, TypedDict


@dataclass
class MongoFilterRules:
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

    raw_key: Sequence[str]
    query_key: Union[str, Sequence, None]
    process: Callable


class PaginateMap(TypedDict, total=False):
    page: str
    per_page: str
    count: str
    max_results: str


class SortMap(TypedDict):
    key: str
    direction: str


class MongoPayload(abc.ABC):
    """Base class for mongo query generation.

    Subclasses must define the `filter_rules` dictionary, mapping fields
    in the database to `FilterRules`. The dictionaries `paginate_map`,
    `sort_map` and `direction_map` are optional. If one of the latter two
    are defined, the other must be defined as well.

    Generally, it shouldn't be necessary to override any methods. Just
    defining rule and mapping dictionaries properly gives the full
    functionality. The inner class `Helpers` contains some generally
    used methods for processing parameters

    NOTE: If the result of a given `FilterRules.process` is `None` for a
    given parameter, it will be ignored, i.e., it is not possible to search
    for null values. If `FilterRules.query_key` expects multiple values,
    each individual `None` will be ignored but the full filter will still be
    used unless all the expected values are `None`.

    Attributes
    ----------
    filter_rules: dict[str, MongoFilterRules]
        Mapping from field name to rules, e.g.,
        `{'a': FilterRules(['b'], '$gt', float)}`
    paginate_map : PaginateMap
        Mapping from pagination arguments to corresponding parser keys, e.g.,
        `{'page': 'page', 'per_page': 'page_size'}`
    sort_map : SortMap
        Mapping from sorting arguments to corresponding parser keys, e.g.,
        `{'key': 'order_by', 'direction': 'order_mode'}`
    direction_map : dict[str, int]
        Mapping from direction values to either 1 (ascending) or -1
        (descending), e.g., `{'ASC': 1, 'DESC': -1}`
    raw_filter : dict
        Input arguments for filtering, e.g., `{'b': '10'}`
    raw_paginate : dict, optional
        Input arguments for pagination, e.g., `{'page_size': 2}`
    raw_sort : dict, optional
        Input arguments for sorting, e.g., `{'key': 'a', 'direction': 'ASC'}`
    """

    filter_rules: Dict[str, MongoFilterRules]
    paginate_map: PaginateMap
    sort_map: SortMap
    direction_map: Dict[str, int]

    class Helpers:
        """Class with static methods used for filter processing"""

        @staticmethod
        def list_of_str(arg):
            """Makes sure to return a list, even if single string is passed.

            Does not change the types of individual elements if a non-string
            sequence is passed. If a single string is passed, a list of size
            one containing the string is created.

            Parameters
            ----------
            arg : str, Sequence
                Argument to turn into list

            Returns
            -------
            list
                Argument as a list
            """
            return _ensure_list(arg, str)

        @staticmethod
        def list_of_int(arg):
            """Makes sure to return a list, even if single integer is passed.

            Does not change the types of individual elements if a sequence
            is passed. If a single integer is passed, a list of size
            one containing the integer is created.

            Parameters
            ----------
            arg : int, Sequence
                Argument to turn into list

            Returns
            -------
            list
                Argument as a list
            """
            return _ensure_list(arg, int)

        @staticmethod
        def list_of_float(arg):
            """Makes sure to return a list, even if single float is passed.

            Does not change the types of individual elements if a sequence
            is passed. If a single float (or integer) is passed, a list of
            size one containing the number is created.

            Parameters
            ----------
            arg : float, int, Sequence
                Argument to turn into list

            Returns
            -------
            list
                Argument as a list
            """
            return _ensure_list(arg, (int, float))

    def __init__(self, filter_args=None, paginate_args=None, sort_args=None):
        """
        Parameters
        ----------
        filter_args : dict
            Input arguments for filtering (usually parsed from `get` methods)
        paginate_args : dict, None
            Input arguments for pagination (usually parsed from `get` methods)
        sort_args : dict, None
            Input arguments for sorting (usually parsed from `get` methods)
        """
        self.raw_filter = filter_args or {}
        self.raw_paginate = paginate_args
        self.raw_sort = sort_args

    @property
    def filter(self):
        """dict: Query ready dictionary, e.g., `{'a': {'$gt': 10.0}}`"""
        output = {
            key: self._generate_filter_value(key)
            for key in self.filter_rules
            if not self._is_null(key)
        }
        return {
            key: value for key, value in output.items() if value is not None
        }

    @property
    def paginate(self):
        """dict: Pagination parameters, e.g., `{'per_page': 2}`"""
        return (
            {
                key: self.raw_paginate[value]
                for key, value in self.paginate_map.items()
                if self.raw_paginate.get(value) is not None
            }
            if self.raw_paginate is not None
            else {}
        )

    @property
    def sort(self):
        """list[tuple] or None: Value for sorting, e.g., `[('a', 1)]`"""
        try:
            keys = self.raw_sort.get(self.sort_map["key"])
            directions = self.raw_sort.get(self.sort_map["direction"])
        except AttributeError:
            return None
        return (
            [
                (key, self.direction_map[direction])
                for key, direction in zip(
                    self.Helpers.list_of_str(keys),
                    self.Helpers.list_of_str(directions),
                )
            ]
            if None not in [keys, directions]
            else None
        )

    def _generate_filter_value(self, key):
        """Creates the value for mongo style query dictionary.

        The values are generated based on the corresponding filter rules.

        Parameters
        ----------
        key : Query dictionary key

        Returns
        -------
        dict
            Value of query dictionary
        """
        rule = self.filter_rules[key]
        value = rule.process(
            *[self.raw_filter.get(key) for key in rule.raw_key]
        )
        if rule.query_key is None:
            return value
        elif isinstance(rule.query_key, str):
            return {rule.query_key: value} if value is not None else None
        return {
            qkey: val
            for qkey, val in zip(rule.query_key, value)
            if val is not None
        } or None

    def _is_null(self, key):
        """Checks if all the raw keys for filter is missing from input.

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
        return all(self.raw_filter.get(rkey) is None for rkey in rule.raw_key)


class SingleObjectPayload(MongoPayload):
    filter_rules = {"aid": MongoFilterRules("aid", None, str)}

    def __init__(self, aid):
        super().__init__({"aid": aid})


def _ensure_list(arg, argtype):
    if isinstance(arg, argtype):
        return [arg]
    return list(arg)
