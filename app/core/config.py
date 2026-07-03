from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):

    DATABASE_URL: str
    SCHEMA: str

    ALLOW_ORIGINS: str

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    FROM_EMAIL: str
    FROM_NAME: str

    APP_NAME: str = 'mail-service'

    model_config = SettingsConfigDict(env_file = BASE_DIR / '.env')

settings = Settings()