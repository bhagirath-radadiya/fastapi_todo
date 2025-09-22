from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.constant import SQLALCHEMY_DATABASE_URL

# Engine with connection pool settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
