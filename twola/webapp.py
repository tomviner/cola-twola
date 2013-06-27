from flask import Flask, render_template

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

if __name__ == '__main__':
    app.run()