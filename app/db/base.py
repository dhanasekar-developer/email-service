from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    metadata = MetaData(settings.SCHEMA)