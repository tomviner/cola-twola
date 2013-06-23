import re
import sys
import json
import requests
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


API_URL = 'http://adaptive-test-api.herokuapp.com/tweets.json'
MAGIC_WORDS_RE = re.compile('coke|coca-cola|diet cola', re.IGNORECASE)

logger = logging.getLogger(__name__)
Base = declarative_base()

class Tweet(Base):
    __tablename__ = 'tweet'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    num_followers = Column(Integer)
    message = Column(String)
    sentiment = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
       return "<Tweet((%s)%s: %s... %s)>" % (self.id, self.user, self.message[:10], self.sentiment)

    # @classmethod
    def store_from_api(self, tweet):
        # self = cls()
        self.user = tweet['user_handle']
        self.num_followers = tweet['followers']
        self.message = tweet['message']
        self.sentiment = tweet['sentiment']
        self.created_at = tweet['created_at']
        self.updated_at = tweet['updated_at']


if 'test' in sys.argv[0]:
    engine = create_engine('sqlite:///:memory:', echo=True)
else:
    engine = create_engine('sqlite:////tmp/twola.db', echo=True)

def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()

def create_db():
    """
    create db if it doesn't exist
    """
    session = get_db_session()
    Base.metadata.create_all(engine)

def add_data():
    session = get_db_session()
    tw = Tweet(
            user="Tom",
            num_followers=3,
            message="I love coke",
            sentiment=0.8,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    session.add(tw)
    session.commit()

def print_data():
    session = get_db_session()
    print session.query(Tweet).all()


def api_tweet_source(n=5):
    for _ in xrange(5):
        response = requests.get(API_URL)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error("API request error: %s", e)
            continue
        yield response.text


def import_tweets_from_json(tweet_source=api_tweet_source):
    """
    takes API response content and saves any new tweets to the db
    """
    session = get_db_session()
    for json_string in tweet_source():
        json_obj = json.loads(json_string)
        # this work for lists and dicts
        if 'error' in json_obj:
            msg = json_obj['error']
            logger.error("API request error: %s", msg)
            continue
        if not isinstance(json_obj, list):
            raise TypeError("Expected a list of tweets, instead found %s" % json_obj)
        for tweet in json_obj:
            Tweet().store_from_api(tweet)
    session.commit()


def load_tweets(just_coke):
    """
    return stored tweets
    """

    session = get_db_session()
    tweets = session.query(Tweet).all()
    if just_coke:
        return [tw for tw in tweets if MAGIC_WORDS_RE.findall(tw.message)]
    return [tw for tw in tweets]


if __name__ == '__main__':
    create_db()
    add_data()
    print_data()

    import_tweets_from_json()