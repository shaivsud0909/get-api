from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import settings
from core.logs import logger


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.debug,
    connect_args=settings.DB_CONNECT_ARGS,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

Base = declarative_base()

logger.info(f"Database connection established with {Base}")


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
