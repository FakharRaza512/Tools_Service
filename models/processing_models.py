from pydantic import BaseModel
from typing import List

# ------------------------
# Request Models
# ------------------------

class SingleTextRequest(BaseModel):
    text: str


class BulkTextRequest(BaseModel):
    texts: List[str]


class ReplaceRequest(BaseModel):
    text: str
    old: str
    new: str


class BulkReplaceRequest(BaseModel):
    texts: List[str]
    old: str
    new: str

# Models for Processing functionality

class KeywordDensityPayload(BaseModel):
    texts: List[str]
    keywords: List[str]


class RelationshipsPayload(BaseModel):
    """
    relationships: list of dicts like:
    [{"subject":"x","object":"y","subject_type":"PERSON","object_type":"ORG"}, ...]
    """
    relationships: List[dict[str, any]]


class IOUPayload(BaseModel):
    a: List[str]
    b: List[str]


class FormatForLLMPayload(BaseModel):
    seed_articles: List[dict[str, any]]  # expects dicts with keys: title, date, link, content
    neighboring: List[dict[str, any]]
    #user_query: optional[str] = ""
