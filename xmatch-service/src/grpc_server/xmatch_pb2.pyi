from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConesearchRequest(_message.Message):
    __slots__ = ("ra", "dec", "radius", "catalog", "nneighbors")
    RA_FIELD_NUMBER: _ClassVar[int]
    DEC_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    CATALOG_FIELD_NUMBER: _ClassVar[int]
    NNEIGHBORS_FIELD_NUMBER: _ClassVar[int]
    ra: float
    dec: float
    radius: float
    catalog: str
    nneighbors: int
    def __init__(self, ra: _Optional[float] = ..., dec: _Optional[float] = ..., radius: _Optional[float] = ..., catalog: _Optional[str] = ..., nneighbors: _Optional[int] = ...) -> None: ...

class ConesearchResponse(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ("ra", "dec", "id", "distance", "catalog")
    RA_FIELD_NUMBER: _ClassVar[int]
    DEC_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    CATALOG_FIELD_NUMBER: _ClassVar[int]
    ra: float
    dec: float
    id: str
    distance: float
    catalog: str
    def __init__(self, ra: _Optional[float] = ..., dec: _Optional[float] = ..., id: _Optional[str] = ..., distance: _Optional[float] = ..., catalog: _Optional[str] = ...) -> None: ...
