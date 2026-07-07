from email.message import EmailMessage
from pathlib import Path
import mimetypes
import aiosmtplib
from app.core.config import settings
from .template import render_template


class EmailSender:

    async def send_email(
        self,
        to_email: list[str],
        subject: str,
        template_name: str,
        context: dict,
        cc_email: list[str] | None = None,
        attachments: list[str] | None = None,
    ):
        
        html = render_template(template_name, context)

        message = EmailMessage()

        message['From'] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
        message['To'] = ', '.join(to_email)
        message['Subject'] = subject

        if cc_email:
            message['Cc'] = ', '.join(cc_email)

        message.set_content('Please enable HTML mail.')
        message.add_alternative(html, subtype = 'html')

        if attachments:

            for file in attachments:

                path = Path(file)

                mime_type, _ = mimetypes.guess_type(path)

                if mime_type:
                    maintype, subtype = mime_type.split('/')

                else:
                    maintype, subtype = "application", "octet-stream"

                with open(path, 'rb') as f:
                    message.add_attachment(
                        f.read(),
                        maintype = maintype,
                        subtype = subtype,
                        filename = path.name
                    )
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=587,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )