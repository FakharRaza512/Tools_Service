from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class LocationText(BaseModel):
    text: str

class LocationTextBulk(BaseModel):
    texts: List[str]

class CoordinatesRequest(BaseModel):
    province: Optional[str] = None
    district: Optional[str] = None
    tehsil: Optional[str] = None