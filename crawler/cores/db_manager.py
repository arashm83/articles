from sqlalchemy import Column, String, create_engine, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()
engine = create_engine('sqlite:///test.db')
session = sessionmaker(bind=engine)

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    url = Column(String)
    abstract = Column(String)
    pdf_url = Column(String)
    create_at = Column(DateTime, default=datetime.now(timezone.utc))

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

class DbManager:
    def __init__(self):
        self.db = session()

    def add_article(self, article: Article):
        try:
            existing = self.get_article(article.title)
            if existing:
                return False
            self.db.add(article)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error adding article: {e}")
            return False

    def get_article(self, title) -> Article:
        return self.db.query(Article).filter(Article.title == title).first()

    def close(self):
        self.db.close()