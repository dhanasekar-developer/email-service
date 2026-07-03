from typing import Annotated
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from fastapi import Depends
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = session()

    try:
        yield db

    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
