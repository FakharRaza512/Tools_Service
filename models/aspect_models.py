# models/aspect_models.py
from pydantic import BaseModel
from typing import List, Dict, Any


# Text input models
# ---------------------------

class TextItem(BaseModel):
    text: str

class TextList(BaseModel):
    texts: List[str]


# ---------------------------
# Keyword density
# ---------------------------
class KeywordDensityRequest(BaseModel):
    keywords: List[str]
    text: str

class KeywordDensityBulkRequest(BaseModel):
    keywords: List[str]
    texts: List[str]


# ---------------------------
# Responses
# ---------------------------
class TrendPoint(BaseModel):
    x: List[Any]
    y: List[Any]
    type: str
    mode: str | None = None
    name: str

class TrendResponse(BaseModel):
    plotData: List[TrendPoint]
# ----------- Common -----------
class DateRange(BaseModel):
    startDate: str  # YYYY-MM-DD
    endDate: str


# ----------- Sentiment Trend -----------
class SentimentRequest(BaseModel):
    keywords: List[str]
    date: DateRange


# ----------- Topic Trend -----------
class TopicTrendRequest(BaseModel):
    topics: List[str]
    date: DateRange


# ----------- Keyword Density -----------
class KeywordDensityRequest(BaseModel):
    keywords: List[str]
    date: DateRange


# ----------- Location Trend -----------
class LocationTrendRequest(BaseModel):
    locations: List[str]
    date: DateRange


# ----------- Response Wrapper -----------
class PlotPoint(BaseModel):
    x: List[Any]
    y: List[Any]
    type: str
    mode: str | None = None
    name: str


class PlotResponse(BaseModel):
    plotData: List[PlotPoint]
