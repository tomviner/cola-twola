from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base


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

