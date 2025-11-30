from pydantic import BaseModel
from typing import List

class LocationText(BaseModel):
    text: str

class LocationTextBulk(BaseModel):
    texts: List[str]
