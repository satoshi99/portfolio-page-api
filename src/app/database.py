from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from utils.env import DB_USER, DB_PASSWORD, DB_DATABASE, DB_HOST

DATABASE = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}?charset=utf8"

engine = create_engine(DATABASE, encoding="utf-8", echo=True)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = SessionLocal.query_property()


def get_db():
    with SessionLocal() as session:
        yield session
