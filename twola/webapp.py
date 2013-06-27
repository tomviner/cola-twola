from flask import Flask, render_template, abort

from models import DbSession


app = Flask(__name__)


@app.route('/')
def tweet_list():
    """
    Displays tweets containing one of the coke keywords
    """
    db = DbSession(test=app.config['TESTING'])
    return render_template(
        'tweet_list.html',
        tweets=db.load_tweets(just_coke=True)
    )


@app.route('/tweet/<int:tweet_id>/')
def tweet_detail(tweet_id):
    """
    Displays details of a single tweet
    """
    db = DbSession(test=app.config['TESTING'])
    tweets = [tw for tw in db.load_tweets(just_coke=True) if tw.id==tweet_id]
    if not tweets:
        abort(404)
    tweet=tweets[0]
    return render_template(
        'tweet_detail.html',
        tweet=tweet
    )

if __name__ == '__main__':
    app.run()