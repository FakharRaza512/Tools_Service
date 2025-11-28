# routes/aspect_route.py

from fastapi import APIRouter
from models.aspect_models import (
    TextItem, TextList,
    KeywordDensityRequest, KeywordDensityBulkRequest,
    TrendResponse
)
from services.aspect_service import AspectService

router = APIRouter(prefix="/aspect", tags=["Aspect Tools"])
service = AspectService()

# =====================================================
# SENTIMENT TREND
# =====================================================

@router.post("/sentiment-trend", response_model=TrendResponse)
def sentiment_trend_single(payload: TextItem):
    return service.sentiment_trend(payload.text)

@router.post("/sentiment-trend/bulk", response_model=TrendResponse)
def sentiment_trend_bulk(payload: TextList):
    return service.sentiment_trend(payload.texts)

# =====================================================
# TOPIC TREND
# =====================================================

@router.post("/topic-trend", response_model=dict)
def topic_trend_single(payload: TextItem):
    return service.topic_trend(payload.text)

@router.post("/topic-trend/bulk", response_model=dict)
def topic_trend_bulk(payload: TextList):
    return service.topic_trend(payload.texts)

# =====================================================
# KEYWORD DENSITY
# =====================================================

@router.post("/keyword-density", response_model=TrendResponse)
def keyword_density_single(payload: KeywordDensityRequest):
    return service.keyword_density(payload.text, payload.keywords)

@router.post("/keyword-density/bulk", response_model=TrendResponse)
def keyword_density_bulk(payload: KeywordDensityBulkRequest):
    return service.keyword_density(payload.texts, payload.keywords)

# =====================================================
# LOCATION TREND
# =====================================================

@router.post("/location-trend", response_model=TrendResponse)
def location_trend_single(payload: TextItem):
    return service.location_trend(payload.text)

@router.post("/location-trend/bulk", response_model=TrendResponse)
def location_trend_bulk(payload: TextList):
    return service.location_trend(payload.texts)
