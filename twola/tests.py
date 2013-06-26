# -*- coding: utf-8 -*-
from models import DbSession


JSON_RESPONSES = [
    # ids: 7, 13
    """[{"created_at":"2012-09-27T16:14:27Z","followers":9,"id":7,"message":"Vimto or Ribena?  You decide!","sentiment":0.2,"updated_at":"2012-09-27T16:14:27Z","user_handle":"@mad4vimto"},{"created_at":"2012-09-27T16:18:09Z","followers":3,"id":13,"message":"I've got to say - Pepsi max is great!","sentiment":0.9,"updated_at":"2012-09-27T16:18:09Z","user_handle":"@tasteless"}]""",
    # an error message, not to be stored in the db
    """{"error":{"message":"Server no respondy"}}""",
    # ids: 3 (contains coke keyword), 13 (dup of above)
    """[{"created_at":"2012-09-27T16:11:15Z","followers":24,"id":3,"message":"Coke is it!","sentiment":1.0,"updated_at":"2012-09-27T16:11:15Z","user_handle":"@coke_snortr"},{"created_at":"2012-09-27T16:18:09Z","followers":3,"id":13,"message":"I've got to say - Pepsi max is great!","sentiment":0.9,"updated_at":"2012-09-27T16:18:09Z","user_handle":"@tasteless"}]"""
]


def mock_tweet_source():
    for json_string in JSON_RESPONSES:
        yield json_string


def test_load_tweets():
    """
    Load some tweets and make sure they are persistent.
    With server error responses and duplicate tweets ignored.
    """
    db = DbSession(test=True)
    db.create_db()

    db.import_tweets_from_json(tweet_source=mock_tweet_source)

    tweets = db.load_tweets(just_coke=False)
    expected_ids = set([3, 7, 13])
    expected_num = len(expected_ids)
    assert len(tweets) == expected_num, "Found %s, expected %s" % (len(tweets), expected_num)
    found_ids = set(tw.id for tw in tweets)
    assert found_ids == expected_ids, "Found %s, expected %s" % (found_ids, expected_ids)

    tweets = db.load_tweets(just_coke=True)
    expected_ids = set([3])
    expected_num = len(expected_ids)
    assert len(tweets) == expected_num, "Found %s, expected %s" % (len(tweets), expected_num)


