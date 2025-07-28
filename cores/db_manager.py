from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from crawler.cores.db_manager import Article
from .auth import hash_password

Base = declarative_base()
engine = create_engine("sqlite:///test.db")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class DbManager:
    def __init__(self):
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        

    def close(self):
        db = self.SessionLocal()
        db.close()

    def get_all_articles(self):
        db = self.SessionLocal()
        try:
            articles = db.query(Article).order_by(Article.create_at).all()
            return articles
        finally:
            db.close()

    def get_article(self, id):
        db = self.SessionLocal()
        try:
            article = db.query(Article).filter(Article.id == id).first()
            return article
        finally:
            db.close()

    def get_user(self, username: str):
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            return user
        finally:
            db.close()

    def create_user(self, username: str, password: str):
        db = self.SessionLocal()
        try:
            user = User(username=username, hashed_password=hash_password(password))
            db.add(user)
            db.commit()
        finally:
            db.close()

def get_db():
        db = DbManager()
        try:
            yield db
        finally:
            db.close()
