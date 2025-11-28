# routes/processing_route.py
from fastapi import APIRouter

from models.processing_models import (
    SingleTextRequest,
    BulkTextRequest,
    ReplaceRequest,
    BulkReplaceRequest
)

from models.processing_models import (
    SingleText, BulkText, KeywordDensityPayload,
    RelationshipsPayload, IOUPayload, FormatForLLMPayload
)
from services.processing_service import ProcessingService

router = APIRouter(prefix="/processing", tags=["Processing Tools"])
svc = ProcessingService()


# ----------------------------------------------------
# BASIC ROUTES
# ----------------------------------------------------

@router.post("/upper")
def convert_upper(payload: SingleTextRequest):
    return {"result": svc.to_upper(payload.text)}

@router.post("/lower")
def convert_lower(payload: SingleTextRequest):
    return {"result": svc.to_lower(payload.text)}

@router.post("/word_count")
def count_words(payload: SingleTextRequest):
    return {"count": svc.word_count(payload.text)}

@router.post("/replace")
def replace_word(payload: ReplaceRequest):
    return {"result": svc.replace_word(payload.text, payload.old, payload.new)}

# ----------------------------------------------------
# BULK ROUTES
# ----------------------------------------------------

@router.post("/bulk/upper")
def bulk_upper(payload: BulkTextRequest):
    return {"results": svc.bulk_upper(payload.texts)}

@router.post("/bulk/lower")
def bulk_lower(payload: BulkTextRequest):
    return {"results": svc.bulk_lower(payload.texts)}

@router.post("/bulk/word_count")
def bulk_word_count(payload: BulkTextRequest):
    return {"counts": svc.bulk_word_count(payload.texts)}

@router.post("/bulk/replace")
def bulk_replace(payload: BulkReplaceRequest):
    return {"results": svc.bulk_replace(payload.texts, payload.old, payload.new)}

# -----------------------
# Cleaning
# -----------------------
@router.post("/clean")
def clean_text(payload: SingleText):
    return {"clean": svc.clean(payload.text)}

@router.post("/clean/bulk")
def clean_text_bulk(payload: BulkText):
    return {"clean": svc.clean_bulk(payload.texts)}

# -----------------------
# Sentences
# -----------------------
@router.post("/sentences")
def split_sentences(payload: SingleText):
    return {"sentences": svc.sentences(payload.text)}

@router.post("/sentences/bulk")
def split_sentences_bulk(payload: BulkText):
    return {"sentences": svc.sentences_bulk(payload.texts)}

# -----------------------
# Entities
# -----------------------
@router.post("/entities")
def entities(payload: SingleText):
    return {"entities": svc.extract_entities_from_text(payload.text)}

@router.post("/entities/bulk")
def entities_bulk(payload: BulkText):
    return {"entities": svc.extract_entities_from_text_bulk(payload.texts)}

@router.post("/entities/from-relationships")
def entities_from_relationships(payload: RelationshipsPayload):
    return {"entities": svc.extract_entities_from_relationships(payload.relationships)}

# -----------------------
# Topics (noun-chunk)
# -----------------------
@router.post("/topic-trend")
def topic_trend(payload: SingleText):
    return {"topics": svc.topic_trend(payload.text)}

@router.post("/topic-trend/bulk")
def topic_trend_bulk(payload: BulkText):
    return {"topics": svc.topic_trend_bulk(payload.texts)}

# -----------------------
# Keyword density
# -----------------------
@router.post("/keyword-density")
def keyword_density(payload: KeywordDensityPayload):
    return {"density": svc.keyword_density(payload.texts, payload.keywords)}

# -----------------------
# Sentiment
# -----------------------
@router.post("/sentiment")
def sentiment(payload: SingleText):
    return {"sentiment": svc.sentiment(payload.text)}

@router.post("/sentiment/bulk")
def sentiment_bulk(payload: BulkText):
    return {"sentiment": svc.sentiment_bulk(payload.texts)}

# -----------------------
# Time extraction
# -----------------------
@router.post("/time")
def time_extract(payload: SingleText):
    years = svc.extract_years(payload.text)
    dates = svc.extract_dates_like(payload.text)
    return {"years": years, "dates": dates}

# -----------------------
# Format for LLM
# -----------------------
@router.post("/format-for-llm")
def format_for_llm(payload: FormatForLLMPayload):
    prompt = svc.format_articles_for_llama(payload.seed_articles, payload.neighboring, payload.user_query or "")
    return {"prompt": prompt}

# -----------------------
# IOU
# -----------------------
@router.post("/iou")
def iou(payload: IOUPayload):
    score = svc.compute_iou(payload.a, payload.b)
    return {"iou": score}
