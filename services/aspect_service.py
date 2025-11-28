# services/aspect_service.py

import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import download as nltk_download
from typing import List, Dict, Any
import re

# --------------- Load spaCy ---------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --------------- Load VADER ---------------
nltk_download("vader_lexicon")
vader = SentimentIntensityAnalyzer()


class AspectService:

    # ====================================================
    # Utility
    # ====================================================

    def _concat(self, text_or_list):
        if isinstance(text_or_list, str):
            return text_or_list
        return " ".join(text_or_list)

    def _sentences(self, text: str):
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # ====================================================
    # SENTIMENT TREND
    # ====================================================

    def sentiment_trend(self, text_or_texts):
        text = self._concat(text_or_texts)
        sentences = self._sentences(text)

        sentiments = [vader.polarity_scores(s)["compound"] for s in sentences]

        return {
            "plotData": [
                {
                    "x": list(range(len(sentiments))),
                    "y": sentiments,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Sentiment Trend",
                }
            ]
        }

    # ====================================================
    # TOPIC TREND (noun chunks)
    # ====================================================

    def topic_trend(self, text_or_texts):
        text = self._concat(text_or_texts)
        doc = nlp(text)

        topics = list(set(chunk.text.lower() for chunk in doc.noun_chunks))

        return {
            "plotData": [
                {
                    "x": list(range(len(topics))),
                    "y": [1] * len(topics),
                    "type": "scatter",
                    "mode": "markers",
                    "name": "Topics",
                }
            ],
            "topics": topics,
        }

    # ====================================================
    # KEYWORD DENSITY
    # ====================================================

    def keyword_density(self, text_or_texts, keywords: List[str]):
        text = self._concat(text_or_texts)
        sentences = self._sentences(text)

        plot_data = []

        for kw in keywords:
            densities = [sentence.lower().count(kw.lower()) for sentence in sentences]

            plot_data.append({
                "x": list(range(len(densities))),
                "y": densities,
                "type": "scatter",
                "mode": "lines+markers",
                "name": kw,
            })

        return {"plotData": plot_data}

    # ====================================================
    # LOCATION TREND
    # ====================================================

    def location_trend(self, text_or_texts):
        text = self._concat(text_or_texts)
        sentences = self._sentences(text)

        plot_data = []
        location_set = set()

        # Pre-detect all unique locations
        for s in sentences:
            doc = nlp(s)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    location_set.add(ent.text)

        for loc in location_set:
            density = [
                1 if loc.lower() in s.lower() else 0
                for s in sentences
            ]

            plot_data.append({
                "x": list(range(len(sentences))),
                "y": density,
                "type": "scatter",
                "mode": "lines+markers",
                "name": loc,
            })

        return {"plotData": plot_data}
