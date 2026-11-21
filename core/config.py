from pathlib import Path
from urllib.parse import quote_plus
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

    DB_HOST: str 
    DB_PORT: int 
    DB_USER: str 
    DB_PASSWORD: str 
    DB_NAME: str 

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


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