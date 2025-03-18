from typing import List, Optional, Union

from pydantic import BaseModel, Field



class Feature(BaseModel):
    name: str
    value: Optional[float] = None
    fid: int
    version: str
