from fastapi import APIRouter, status
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
    print('request:0---------------',request)
    mail_service.insert_email_record(request, db)
    return 1
    