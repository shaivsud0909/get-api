from pathlib import Path
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit
from fastapi.datastructures import URL
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]



class Settings(BaseSettings):
    # Application
    title: str = "Boiler"
    description: str = "Boilerplate FastAPI project"
    version: str = "1.0.0"
    debug: bool = False

    port: int = 8000

    # Either a full connection URL (injected by Inframan as DATABASE_URL)...
    database_url: str | None = None
    # ...or the individual parts (local development / docker-compose).
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None
    # Postgres schema the app's tables live in (isolates it on a shared database).
    DB_SCHEMA: str = "public"

    # Connection pool: kept deliberately small so the app holds as few
    # connections as possible on the shared, small Postgres instance.
    DB_POOL_SIZE: int = 1        # connections kept open per process
    DB_MAX_OVERFLOW: int = 2     # extra connections opened only under load
    DB_POOL_TIMEOUT: int = 30    # seconds to wait for a free connection
    DB_POOL_RECYCLE: int = 1800  # seconds before a connection is replaced

    @property
    def DATABASE_URL(self) -> str:
        if self.database_url:
            parts = urlsplit(self.database_url)
            # asyncpg does not understand libpq's sslmode & co.; drop them.
            query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k not in {"sslmode", "sslrootcert", "sslcert", "sslkey"}])
            return urlunsplit(("postgresql+asyncpg", parts.netloc, parts.path, query, parts.fragment))
        return f"postgresql+asyncpg://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_CONNECT_ARGS(self) -> dict:
        return {"server_settings": {"search_path": self.DB_SCHEMA}}


    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str
    ALGORITHM: str = "HS256"


    # Payment gateway (Razorpay)
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    PAYMENT_CURRENCY: str = "INR"


    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()