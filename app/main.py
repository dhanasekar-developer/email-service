from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.logging import logger
from app.common.request_exeption_handler import register_exeption_handler
from fastapi.middleware.cors import CORSMiddleware
from app.email.router import router as email_router
from app.email.worker import main as email_worker
import asyncio
from app.middleware.api_key import APIKeyMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('App starting')
    asyncio.create_task(email_worker())

    yield
    logger.info('App stoping')

app = FastAPI(
    title=settings.APP_NAME,
    version='1.0.0',
    lifespan=lifespan
)

register_exeption_handler(app)

app.add_middleware(
    CORSMiddleware,
    APIKeyMiddleware,
    allow_origins = settings.ALLOW_ORIGINS.split(','),
    allow_methods = [ "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS" ],
    allow_credentials = True,
    allow_headers = [ '*' ],
)

app.include_router(email_router)

@app.get('/')
def root():
    return {
        'message': 'Chat App Is Runing'
    }

@app.get('/health')
def health():
    return {
        'status': 'healthy'
    }