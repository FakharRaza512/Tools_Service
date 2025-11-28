from pydantic import BaseModel
from typing import List, Any, Optional

class TextPayload(BaseModel):
    text: str

class DetailsPayload(BaseModel):
    details: str

class LocationPayload(BaseModel):
    read_more: str
    header: str

class TimePayload(BaseModel):
    data: dict
    timeData: dict

class TopicPayload(BaseModel):
    articles: List[str]
    num_topics: int = 5
    num_words: int = 10
    max_df: float = 0.95
    min_df: float = 0.05

class FullProcessPayload(BaseModel):
    header: str
    summary: str
    details: str
