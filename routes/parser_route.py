from fastapi import APIRouter
from services.parser_service import ParserService
from models.parser_models import *

router = APIRouter(prefix="/parser", tags=["Parser Tools"])


@router.post("/clean")
def clean_endpoint(payload: TextPayload):
    return ParserService.clean_text(payload.text)


@router.post("/split-sentences")
def split_sentences(payload: TextPayload):
    return ParserService.split_sentences(payload.text)


@router.post("/extract-locations")
def extract_locations(payload: LocationPayload):
    return ParserService.extract_location(payload.read_more, payload.header)


@router.post("/extract-time")
def extract_time(payload: TimePayload):
    return ParserService.extract_time(payload.data, payload.timeData)


@router.post("/extract-topics")
def extract_topics(payload: DetailsPayload):
    return ParserService.extract_topics(payload.details)


@router.post("/topic/lda")
def lda_topics(payload: TopicPayload):
    return ParserService.topic_lda(
        payload.articles,
        payload.num_topics,
        payload.num_words,
        payload.max_df,
        payload.min_df
    )


@router.post("/topic/nmf")
def nmf_topics(payload: TopicPayload):
    return ParserService.topic_nmf(
        payload.articles,
        payload.num_topics,
        payload.num_words,
        payload.max_df,
        payload.min_df
    )


@router.post("/sentiment")
def sentiment(payload: TextPayload):
    return ParserService.sentiment(payload.text)


@router.post("/sentiment/tb")
def sentiment_tb(payload: TextPayload):
    return ParserService.sentiment_tb(payload.text)


@router.post("/sentiment/vader")
def sentiment_vader(payload: TextPayload):
    return ParserService.sentiment_vader(payload.text)


@router.post("/timetags")
def timetags(payload: dict):
    tags = payload.get("tags", [])
    text_type = payload.get("textType", "details")
    return ParserService.time_tags(tags, text_type)


@router.post("/process-full")
def process_full(payload: FullProcessPayload):
    return ParserService.full_process(payload.header, payload.summary, payload.details)
