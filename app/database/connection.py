from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
 
from core.config import settings
from core.logs import logger


engine = create_engine(settings.DATABASE_URL,echo=True)

#It creates a factory that gives you database sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# tracks all models (User, etc.)
# collects metadata
# used to create tables
Base = declarative_base()

logger.info(f"Database connection established with {Base}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
