from pydantic import BaseModel
from app.email.models import TemplateName

class SendEmailRequest(BaseModel):

    to_email: list[str]

    cc_email: list[str] | None = None

    subject: str

    template_name: TemplateName

    context: dict

    attachments: list[str] | None = None