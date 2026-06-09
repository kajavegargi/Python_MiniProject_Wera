from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base

DB_URL = "sqlite:///wera.db"

engine = create_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,      # recycle connections every 30 min
    pool_timeout=30,
)

SessionFactory = sessionmaker(bind=engine)
ScopedSession  = scoped_session(SessionFactory)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return ScopedSession()


def close_session():
    ScopedSession.remove()