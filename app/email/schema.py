from pydantic import BaseModel

class SendEmailRequest(BaseModel):

    to_email: list[str]

    cc_email: list[str] | None = None

    subject: str

    template_name: str

    context: dict

    attachments: list[str] | None = None