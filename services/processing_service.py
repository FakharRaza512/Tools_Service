class ProcessingService:

    # ----------------------------------------------------
    # BASIC OPS
    # ----------------------------------------------------
    def to_upper(self, text: str) -> str:
        return text.upper()

    def to_lower(self, text: str) -> str:
        return text.lower()

    def word_count(self, text: str) -> int:
        return len(text.split())

    def replace_word(self, text: str, old: str, new: str) -> str:
        return text.replace(old, new)

    # ----------------------------------------------------
    # BULK OPS
    # ----------------------------------------------------
    def bulk_upper(self, texts: list[str]) -> list[str]:
        return [t.upper() for t in texts]

    def bulk_lower(self, texts: list[str]) -> list[str]:
        return [t.lower() for t in texts]

    def bulk_word_count(self, texts: list[str]) -> list[int]:
        return [len(t.split()) for t in texts]

    def bulk_replace(self, texts: list[str], old: str, new: str) -> list[str]:
        return [t.replace(old, new) for t in texts]
    # ====================================================
    # PROCESSING HELPERS
    # ====================================================

    # services/processing_service.py
import re
from typing import List, Dict, Any
from collections import Counter

# Try safe import / download patterns for spaCy & NLTK/TextBlob
try:
    import spacy
except Exception:
    spacy = None

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk import download as nltk_download
except Exception:
    SentimentIntensityAnalyzer = None
    nltk_download = None

try:
    from textblob import TextBlob
except Exception:
    TextBlob = None

# Safe spaCy loader
def _load_spacy_model(name="en_core_web_sm"):
    global spacy
    if spacy is None:
        import spacy as _spacy
        spacy = _spacy
    try:
        return spacy.load(name)
    except Exception:
        # download via spacy.cli if not present
        try:
            import spacy.cli
            spacy.cli.download(name)
            return spacy.load(name)
        except Exception:
            # final fallback: return None - endpoints should handle None gracefully
            return None

nlp = _load_spacy_model()

# Safe NLTK Vader setup
if SentimentIntensityAnalyzer is not None:
    try:
        _vader = SentimentIntensityAnalyzer()
    except Exception:
        if nltk_download:
            nltk_download("vader_lexicon")
            _vader = SentimentIntensityAnalyzer()
        else:
            _vader = None
else:
    _vader = None


class ProcessingService:
    """Pure text-processing helpers aggregated from NewsNet + NAaaS (no I/O)."""

    # ---------------------
    # CLEANING / NORMALIZATION
    # ---------------------
    def clean(self, text: str) -> str:
        """Lightweight cleaning: collapse whitespace, strip, remove repeated punctuation."""
        if not isinstance(text, str):
            return ""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"([!?.,])\1+", r"\1", text)  # collapse repeated punctuation
        return text.strip()

    def clean_bulk(self, texts: List[str]) -> List[str]:
        return [self.clean(t) for t in texts]

    # ---------------------
    # SENTENCE SPLITTING
    # ---------------------
    def sentences(self, text: str) -> List[str]:
        if not isinstance(text, str):
            return []
        # Prefer spaCy sentence segmentation if available
        if nlp:
            doc = nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        # fallback simple split
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if p.strip()]

    def sentences_bulk(self, texts: List[str]) -> List[List[str]]:
        return [self.sentences(t) for t in texts]

    # ---------------------
    # NAMED ENTITY / ENTITY EXTRACTION
    # ---------------------
    def extract_entities_from_text(self, text: str) -> List[Dict[str, str]]:
        """Return list of (text, label) dicts for selected entity types."""
        if not isinstance(text, str):
            return []
        if not nlp:
            return []
        doc = nlp(text)
        out = []
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "ORG", "GPE", "LOC", "EVENT"):
                out.append({"text": ent.text, "label": ent.label_})
        return out

    def extract_entities_from_text_bulk(self, texts: List[str]) -> List[List[Dict[str, str]]]:
        return [self.extract_entities_from_text(t) for t in texts]

    def extract_entities_from_relationships(self, relationships: List[Dict[str, Any]]) -> List[str]:
        """
        Given relationships (list of dicts with keys 'subject'/'object'), return unique entity names (lowercase).
        This mirrors NAaaS extract_entities that extracts entities from relationships.
        """
        if not relationships:
            return []
        entities = set()
        for rel in relationships:
            if not isinstance(rel, dict):
                continue
            if "subject" in rel and isinstance(rel["subject"], str):
                entities.add(rel["subject"].lower())
            if "object" in rel and isinstance(rel["object"], str):
                entities.add(rel["object"].lower())
        return sorted(list(entities))

    # ---------------------
    # TOPICS - noun-chunk based (lightweight)
    # ---------------------
    def topic_trend(self, text: str) -> List[str]:
        if not isinstance(text, str):
            return []
        if not nlp:
            # fallback: return most common words excluding stopwords-ish short tokens
            tokens = [t.lower() for t in re.findall(r"\w+", text) if len(t) > 3]
            counts = Counter(tokens)
            return [w for w, _ in counts.most_common(5)]
        doc = nlp(text)
        topics = list({chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 1})
        return topics

    def topic_trend_bulk(self, texts: List[str]) -> List[List[str]]:
        return [self.topic_trend(t) for t in texts]

    # ---------------------
    # KEYWORD DENSITY (simple)
    # ---------------------
    def keyword_density(self, texts: List[str], keywords: List[str]) -> List[Dict[str, Dict[str, float]]]:
        results = []
        kws = [k.lower() for k in keywords]
        for text in texts:
            text_lower = (text or "").lower()
            words = re.findall(r"\w+", text_lower)
            total = max(1, len(words))
            density_map = {}
            for kw in kws:
                count = text_lower.count(kw)
                density_map[kw] = {"count": count, "density": count / total}
            results.append(density_map)
        return results

    # ---------------------
    # SENTIMENT - combine VADER + TextBlob (if available)
    # ---------------------
    def sentiment(self, text: str) -> Dict[str, float]:
        """Return sentiment dict that includes vader (compound) and textblob (polarity) and average."""
        if not isinstance(text, str):
            return {"vader": 0.0, "textblob": 0.0, "average": 0.0}
        vader_score = 0.0
        tb_score = 0.0
        if _vader:
            try:
                vs = _vader.polarity_scores(text)
                vader_score = vs.get("compound", 0.0)
            except Exception:
                vader_score = 0.0
        if TextBlob:
            try:
                tb = TextBlob(text).sentiment.polarity  # -1..1
                tb_score = tb
            except Exception:
                tb_score = 0.0
        # normalize both to -1..1 (they already are), compute mean
        avg = 0.0
        try:
            avg = (vader_score + tb_score) / 2.0
        except Exception:
            avg = vader_score or tb_score or 0.0
        return {"vader": vader_score, "textblob": tb_score, "average": avg}

    def sentiment_bulk(self, texts: List[str]) -> List[Dict[str, float]]:
        return [self.sentiment(t) for t in texts]

    # ---------------------
    # TIME EXTRACTION (lightweight)
    # ---------------------
    def extract_years(self, text: str) -> List[str]:
        """Extract 4-digit years like 1980, 2024 using regex (mirrors NewsNet simple year extraction)."""
        if not isinstance(text, str):
            return []
        matches = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
        return matches

    def extract_dates_like(self, text: str) -> List[str]:
        """
        Lightweight date extraction patterns (DD Month YYYY, Month DD, YYYY, ISO).
        This is intentionally simple — for robust extraction use datefinder / dateparser.
        """
        if not isinstance(text, str):
            return []
        results = set()
        # ISO-like dates
        iso_matches = re.findall(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
        for m in iso_matches:
            results.add(m)
        # Month name patterns e.g. 'March 5, 2024' or '5 March 2024'
        month_pat = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b'
        more = re.findall(rf'(\d{{1,2}}\s+{month_pat}\s+\d{{4}})', text, flags=re.IGNORECASE)
        for m in more:
            results.add(m[0] if isinstance(m, tuple) else m)
        more2 = re.findall(rf'({month_pat}\s+\d{{1,2}},?\s+\d{{4}})', text, flags=re.IGNORECASE)
        for m in more2:
            results.add(m[0] if isinstance(m, tuple) else m)
        return sorted(list(results))

    # ---------------------
    # FORMAT FOR LLM (format articles -> big prompt)
    # ---------------------
    def format_articles_for_llama(self, seed_articles: List[Dict[str, Any]], neighboring: List[Dict[str, Any]], user_query: str = "") -> str:
        system_prompt = (
            "You are an AI that summarizes multiple articles into a single, comprehensive response. "
            "Your response should include:\n"
            "1. A well-structured summary of key information from all articles.\n"
            "2. A timeline of events (if applicable) in chronological order.\n"
            "3. Sources (URLs) for credibility. Keep sources at the end.\n"
            "4. Keep the response well-formatted and informative.\n\n"
            "IMPORTANT: FORMAT YOUR RESPONSE WITH MARKDOWN:\n"
            "- Use # for main headings\n"
            "- Use ## for subheadings\n"
            "- Use **bold text** for emphasis\n"
            "- Use bullet points (- or *) for lists\n"
            "- Use numbered lists where appropriate\n"
        )
        if user_query:
            system_prompt += f"\nFOCUS ON ANSWERING THIS SPECIFIC QUERY: {user_query}\n\n"
        system_prompt += "\nHere are the articles:\n\n"
        system_prompt += "**Main Articles:**\n\n"
        for article in seed_articles:
            title = article.get("title", "")
            date = article.get("date", "")
            link = article.get("link", "")
            content = article.get("content", "")
            snippet = (content[:500] + "...") if content else ""
            system_prompt += f"**Title:** {title}\n**Published Date:** {date}\n**Source:** {link}\n**Content:** {snippet}\n\n"
        system_prompt += "**Relevant Articles (Neighbors):**\n\n"
        for article in neighboring:
            title = article.get("title", "")
            date = article.get("date", "")
            link = article.get("link", "")
            content = article.get("content", "")
            snippet = (content[:500] + "...") if content else ""
            system_prompt += f"**Title:** {title}\n**Published Date:** {date}\n**Source:** {link}\n**Content:** {snippet}\n\n"
        return system_prompt

    # ---------------------
    # IOU helper (set intersection over union)
    # ---------------------
    def compute_iou(self, a: List[str], b: List[str]) -> float:
        set_a = set(a or [])
        set_b = set(b or [])
        if not set_a and not set_b:
            return 0.0
        inter = len(set_a & set_b)
        union = len(set_a | set_b)
        return inter / union if union else 0.0
