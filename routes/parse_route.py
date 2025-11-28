from fastapi import APIRouter
from pydantic import BaseModel
from services.parse_service import ParserService

router = APIRouter(prefix="/parser", tags=["Parser Tools"])
service = ParserService()

# ------------------------
# Request Models
# ------------------------
class TextItem(BaseModel):
    text: str

class TextList(BaseModel):
    texts: list[str]


# ------------------------
# CLEAN
# ------------------------
@router.post("/clean")
def clean_text(payload: TextItem):
    return {"clean": service.clean(payload.text)}

@router.post("/clean/bulk")
def clean_text_bulk(payload: TextList):
    return {"clean": service.clean_bulk(payload.texts)}

# ------------------------
# LOCATION
# ------------------------
@router.post("/location")
def extract_location(payload: TextItem):
    return {"location": service.get_location(payload.text)}

@router.post("/location/bulk")
def extract_location_bulk(payload: TextList):
    return {"location": service.get_location_bulk(payload.texts)}

# ------------------------
# TIME
# ------------------------
@router.post("/time")
def extract_time(payload: TextItem):
    return {"time": service.get_time(payload.text)}

@router.post("/time/bulk")
def extract_time_bulk(payload: TextList):
    return {"time": service.get_time_bulk(payload.texts)}

# ------------------------
# TOPICS
# ------------------------
@router.post("/topics")
def extract_topics(payload: TextItem):
    return {"topics": service.get_topics(payload.text)}

@router.post("/topics/bulk")
def extract_topics_bulk(payload: TextList):
    return {"topics": service.get_topics_bulk(payload.texts)}

# ------------------------
# SENTIMENT
# ------------------------
@router.post("/sentiment")
def extract_sentiment(payload: TextItem):
    return {"sentiment": service.get_sentiment(payload.text)}

@router.post("/sentiment/bulk")
def extract_sentiment_bulk(payload: TextList):
    return {"sentiment": service.get_sentiment_bulk(payload.texts)}
