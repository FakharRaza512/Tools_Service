import re
import spacy
from spacy.cli import download
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import download as nltk_download

# ---------------------
# Load spaCy safely
# ---------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ---------------------
# Load NLTK Vader
# ---------------------
nltk_download("vader_lexicon")
vader = SentimentIntensityAnalyzer()


class ParserService:

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------
    def clean(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def clean_bulk(self, texts: list[str]) -> list[str]:
        return [self.clean(t) for t in texts]

    # ---------------------------------------------------------
    # LOCATION (simple pattern-based extractor)
    # ---------------------------------------------------------
    def get_location(self, text: str):
        if not isinstance(text, str):
            return None
        
        doc = nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        if len(locations) == 0:
            return None
        return list(set(locations))  # unique

    def get_location_bulk(self, texts: list[str]):
        return [self.get_location(t) for t in texts]

    # ---------------------------------------------------------
    # TIME EXTRACTION
    # ---------------------------------------------------------
    def get_time(self, text: str):
        if not isinstance(text, str):
            return None
        matches = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
        return matches if matches else None

    def get_time_bulk(self, texts: list[str]):
        return [self.get_time(t) for t in texts]

    # ---------------------------------------------------------
    # TOPICS (noun-chunk based)
    # ---------------------------------------------------------
    def get_topics(self, text: str):
        if not isinstance(text, str):
            return []
        doc = nlp(text)
        return list(set(chunk.text.lower() for chunk in doc.noun_chunks))

    def get_topics_bulk(self, texts: list[str]):
        return [self.get_topics(t) for t in texts]

    # ---------------------------------------------------------
    # SENTIMENT
    # ---------------------------------------------------------
    def get_sentiment(self, text: str):
        if not isinstance(text, str):
            return {"compound": 0}
        return vader.polarity_scores(text)

    def get_sentiment_bulk(self, texts: list[str]):
        return [self.get_sentiment(t) for t in texts]
