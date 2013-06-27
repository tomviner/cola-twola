import os
import re
import sys
import json
import requests
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, \
    create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


API_URL = 'http://adaptive-test-api.herokuapp.com/tweets.json'
MAGIC_WORDS = r'coke|coca-cola|diet cola'
MAGIC_WORDS_RE = re.compile(MAGIC_WORDS, re.IGNORECASE)


logger = logging.getLogger(__name__)
logging.basicConfig()
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

    @classmethod
    def from_api_data(cls, tweet):
        return cls(
            id=tweet['id'],
            user=tweet['user_handle'],
            num_followers=tweet['followers'],
            message=tweet['message'],
            sentiment=tweet['sentiment'],
            created_at=datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            updated_at=datetime.strptime(tweet['updated_at'], '%Y-%m-%dT%H:%M:%SZ'),
        )


class DbSession(object):
    """
    Database wrapper, so we keep a reference to the engine used
    """
    def __init__(self, test=False):
        self.test = test
        self.test_db_path = '/tmp/twola-testing.db'
        if test:
            self.engine = create_engine('sqlite:///'+self.test_db_path, echo=False)
        else:
            self.engine = create_engine('sqlite:////tmp/twola.db', echo=False)

    def get_db_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def create_db(self):
        """
        create db if it doesn't exist
        """
        # use blunt force to ensure a fresh test db each time
        if self.test and os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        session = self.get_db_session()
        Base.metadata.create_all(self.engine)


    def api_tweet_source(self, n=2):
        """
        make n requests to the API. log errors but don't raise exceptions
        yielding json bodies as unicode
        """
        for _ in xrange(n):
            response = requests.get(API_URL)
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error("API request error: %s", e)
                continue
            yield response.text

    def import_tweets_from_json(self, tweet_source=None):
        """
        takes API response content and saves any new tweets to the db
        """
        if tweet_source is None:
            tweet_source = self.api_tweet_source
        session = self.get_db_session()
        for json_string in tweet_source():
            json_obj = json.loads(json_string)
            # this works for lists and dicts
            if 'error' in json_obj:
                msg = json_obj['error']
                logger.error("API request error: %s", msg)
                continue
            if not isinstance(json_obj, list):
                raise TypeError("Expected a list of tweets, instead found %s" % json_obj)
            for tweet in json_obj:
                # only add if not already in db
                if not session.query(Tweet).filter('id=%s' % tweet['id']).count():
                    tweet_obj = Tweet.from_api_data(tweet)
                    session.add(tweet_obj)
        session.commit()

    def load_tweets(self, just_coke):
        """
        return stored tweets
        """

        session = self.get_db_session()
        tweets = session.query(Tweet).order_by(desc(Tweet.sentiment))
        if just_coke:
            # TODO:
            # make this work with either an SQL regex query, or a
            # case insensitive list of OR clauses
            return [tw for tw in tweets if MAGIC_WORDS_RE.findall(tw.message)]
        session.close()
        return tweets.all()

    def get_tweet_by_id(self, id):
        """
        Collect a tweet by id
        """
        session = self.get_db_session()
        return session.query(Tweet).get(id)


if __name__ == '__main__':
    db = DbSession()
    db.create_db()
    db.import_tweets_from_json()
    print len(db.load_tweets(just_coke=False)), 'total'
    print len(db.load_tweets(just_coke=True)), 'tweets with coke'
    print [t.id for t in db.load_tweets(just_coke=False)]
