from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float  # Import Boolean and Float
from database import Base

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    agency = Column(String, nullable=False)
    section = Column(String, nullable=False)
    author = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    headline = Column(String, nullable=False)
    link = Column(String, unique=True, nullable=False)
    is_political = Column(Boolean, nullable=False, default=False)  # Add the new column
    sentiment_score = Column(Float, nullable=True)  # Add the sentiment_score column
    content = Column(String, nullable=True)  # Optionally keep the content field

    def __repr__(self):
        return f"<Article(agency={self.agency}, section={self.section}, author={self.author}, date={self.date}, headline={self.headline}, link={self.link}, is_political={self.is_political}, sentiment_score={self.sentiment_score})>"