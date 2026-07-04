from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from .service import EmailService
from app.db.database import db_dependency
from .schema import SendEmailRequest

router = APIRouter(
    prefix='/email',
    tags=['Email']
)

mail_service = EmailService()

@router.post('/send_email', status_code=status.HTTP_200_OK)
def send_email(request: SendEmailRequest, db: db_dependency):
    
    email_record = mail_service.insert_email_record(request, db)

    if email_record:
        return JSONResponse(
            status_code=status.HTTP_200_OK
        )

    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'detail': 'Something went wrong, Please try again!'
            }
        )
    