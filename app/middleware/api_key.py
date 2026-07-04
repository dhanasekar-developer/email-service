from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class APIKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.url.path in ("/", "/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)
        
        api_key = request.headers.get('x-api-key')

        if api_key != settings.API_KEY:

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    'detail': 'Invalid API Key'
                }
            )
        
        response = await call_next(request)

        return response
