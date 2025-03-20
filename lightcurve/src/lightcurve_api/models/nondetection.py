from typing import List, Optional, Union

from pydantic import BaseModel, Field


class NonDetection(BaseModel):
    aid: Optional[str] = None
    tid: str
    sid: Optional[str] = None
    oid: Optional[str] = None
    mjd: float
    fid: int
    diffmaglim: Optional[float] = None

    def __hash__(self):
        return hash((self.oid, self.fid, self.mjd))

    def __eq__(self, other):
        return (self.oid, self.fid, self.mjd) == (
            other.oid,
            other.fid,
            other.mjd,
        )