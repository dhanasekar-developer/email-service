from sqlalchemy.orm import Session
from sqlalchemy import text
from .schema import SendEmailRequest
from .models import EmailRecord
from .sender import EmailSender

class EmailService:

    def insert_email_record(self, payload: SendEmailRequest, db: Session):

        email_record = EmailRecord(
            to_email=payload.to_email,
            cc_email=payload.cc_email,
            subject=payload.subject,
            template_name=payload.template_name,
            context=payload.context,
            attachments=payload.attachments,
        )

        db.add(email_record)
        db.flush()

        db.execute(
            text(
                "NOTIFY email_channel, :payload"
            ),
            {
                'payload': str(email_record.id)
            }
        )

        db.commit()

        return email_record