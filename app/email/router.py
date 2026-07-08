from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from .service import EmailService
from app.db.database import db_dependency
from .schema import SendEmailRequest
import asyncio

router = APIRouter(
    prefix='/email',
    tags=['Email']
)

mail_service = EmailService()

@router.post('/send_email', status_code=status.HTTP_200_OK)
def send_email(request: SendEmailRequest, db: db_dependency):
    print('request--------------',request)
    email_record = mail_service.insert_email_record(request, db)

    if email_record:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'Email sent successfully!'
            }
        )

    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'detail': 'Something went wrong, Please try again!'
            }
        )
    

@router.get("/smtp-test")
async def smtp_test():
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("smtp.gmail.com", 587),
            timeout=10,
        )
        writer.close()
        await writer.wait_closed()
        return {"status": "connected"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}