import sys, os
from typing import List

# Add ProcessingTools to PYTHONPATH
BASE_PT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Parsing_Tools"))
sys.path.append(BASE_PT)

from Parsing_Tools.parser import clean, sentences, extract_topics, Lda, topic_model_nmf, Get_location, Get_Time
from Parsing_Tools.sentiment import get_sentiment, get_sentiment_tb, get_sentiment_nl
from Parsing_Tools.timetag import createTags, addTextType
# 
class ParserService:

    @staticmethod
    def clean_text(doc: str):
        return clean(doc)

    @staticmethod
    def split_sentences(text: str):
        return sentences(text)

    @staticmethod
    def extract_location(read_more: str, header: str):
        return Get_location(read_more, header)

    @staticmethod
    def extract_time(data: dict, timeData: dict):
        return Get_Time(data, timeData)

    @staticmethod
    def extract_topics(details: str):
        return extract_topics(details)

    @staticmethod
    def topic_lda(articles: List[str], num_topics, num_words, max_df, min_df):
        return Lda(articles, num_topics, num_words, max_df, min_df)

    @staticmethod
    def topic_nmf(articles: List[str], num_topics, num_words, max_df, min_df):
        return topic_model_nmf(articles, num_topics, num_words, max_df, min_df)

  # @staticmethod
  #  def sentiment(text: str):
  #      return get_sentiment(text)#

  #  @staticmethod
  #  def sentiment_tb(text: str):
  #     return get_sentiment_tb(text)

  #  @staticmethod
  #  def sentiment_vader(text: str):
  #      return get_sentiment_nl(text)

    @staticmethod
    def time_tags(tags: list, text_type: str):
        tags_out = createTags(tags)
        return addTextType(tags_out, text_type)

    @staticmethod
    def full_process(header: str, summary: str, details: str):
        cleaned = clean(details)
        topics = extract_topics(details)
        sentiment_score = get_sentiment(details)
        location = Get_location(details, header)
        time_data = Get_Time({"header": header, "summary": summary, "details": details}, {})

        return {
            "cleaned": cleaned,
            "topics": topics,
            "sentiment": sentiment_score,
            "location": location,
            "time": time_data
        }
