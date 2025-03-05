from sqlalchemy import Column, Integer, String, DateTime
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

    def __repr__(self):
        return f"<Article(agency={self.agency}, section={self.section}, author={self.author}, date={self.date}, headline={self.headline}, link={self.link})>"