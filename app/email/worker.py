import asyncio
from uuid import UUID
import asyncpg
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update

from .models import EmailRecord, StatusType
from .sender import EmailSender
from app.db.database import session
from app.core.config import settings
from app.core.logging import logger

sender = EmailSender()

RETRY_DELAY = [1, 1, 5, 10, 15, 30]
MAX_RETRY = 5


async def process_email(id: UUID):

    with session() as db:
        try:
            email = db.execute(
                update(EmailRecord)
                .where(
                    EmailRecord.id == id,
                    EmailRecord.status == StatusType.PENDING
                )
                .values(status=StatusType.PROCESSING)
                .returning(EmailRecord)
            ).scalar_one_or_none()

            db.commit()

        except Exception:
            db.rollback()
            raise

        if not email:
            return

        email_snapshot = {
            "to_email": email.to_email,
            "cc_email": email.cc_email,
            "subject": email.subject,
            "template_name": email.template_name,
            "context": email.context,
            "attachments": email.attachments,
            "retry_count": email.retry_count,
        }

    send_error: Exception | None = None

    try:
        logger.info(f"Sending email to {email_snapshot['to_email']}")

        await sender.send_email(
            to_email=email_snapshot["to_email"],
            cc_email=email_snapshot["cc_email"],
            subject=email_snapshot["subject"],
            template_name=email_snapshot["template_name"],
            context=email_snapshot["context"],
            attachments=email_snapshot["attachments"],
        )

        logger.info("Send completed")

    except Exception as e:
        send_error = e
        logger.error(f"Send failed: {type(e).__name__}: {e}")

    with session() as db:
        try:
            if send_error is None:
                logger.info(f"Email sent successfully id: {id}")
                db.execute(
                    update(EmailRecord)
                    .where(EmailRecord.id == id)
                    .values(
                        status=StatusType.SENT,
                        sent_at=datetime.now(timezone.utc),
                        last_error=None,
                    )
                )
            else:
                retry_count = email_snapshot["retry_count"]

                if retry_count >= MAX_RETRY:
                    logger.warning(f"Email permanently failed id: {id}")
                    db.execute(
                        update(EmailRecord)
                        .where(EmailRecord.id == id)
                        .values(
                            status=StatusType.FAILED,
                            last_error=str(send_error),
                        )
                    )
                else:
                    delay = RETRY_DELAY[min(retry_count, len(RETRY_DELAY) - 1)]
                    logger.info(f"Retry {retry_count + 1} scheduled in {delay}min id: {id}")
                    db.execute(
                        update(EmailRecord)
                        .where(EmailRecord.id == id)
                        .values(
                            status=StatusType.PENDING,
                            last_error=str(send_error),
                            retry_count=retry_count + 1,
                            next_retry_at=(
                                datetime.now(timezone.utc) + timedelta(minutes=delay)
                            ),
                        )
                    )

            db.commit()

        except Exception:
            db.rollback()
            raise


async def safe_email_process(id: UUID | str):
    logger.info(f"Processing email id: {id}")
    try:
        if not isinstance(id, UUID):
            id = UUID(str(id))
    except (ValueError, AttributeError) as e:
        logger.exception(f"Invalid UUID in email payload: {e}")
        return

    try:
        await process_email(id)
    except Exception:
        logger.exception(f"Unexpected email worker error for id: {id}")


def notification_handler(connection, pid, channel, payload):
    logger.info(f"Notification received — payload: {payload}")
    loop = asyncio.get_event_loop()
    loop.create_task(safe_email_process(payload))


async def retry_pending():
    while True:
        try:
            with session() as db:
                ids = db.execute(
                    select(EmailRecord.id)
                    .where(
                        EmailRecord.status == StatusType.PENDING,
                        EmailRecord.next_retry_at <= datetime.now(timezone.utc),
                        EmailRecord.retry_count > 0,
                    )
                ).scalars().all()

            await asyncio.gather(
                *(safe_email_process(id) for id in ids)
            )

        except Exception:
            logger.exception("Error in retry_pending loop")

        await asyncio.sleep(5)


async def recover_pending():
    try:
        with session() as db:
            ids = db.execute(
                select(EmailRecord.id)
                .where(
                    EmailRecord.status == StatusType.PENDING,
                    EmailRecord.retry_count == 0,
                )
            ).scalars().all()

        await asyncio.gather(
            *(safe_email_process(id) for id in ids)
        )

    except Exception:
        logger.exception("Error in recover_pending")


async def start_listener():
    while True:
        conn = None
        try:
            conn = await asyncpg.connect(settings.DATABASE_URL)
            await conn.execute("LISTEN email_channel")
            await conn.add_listener("email_channel", notification_handler)
            logger.info("Listening for email notifications on email_channel...")

            while True:
                await asyncio.sleep(3600)

        except Exception:
            logger.exception("Listener crashed — restarting in 5s")
            await asyncio.sleep(5)

        finally:
            if conn and not conn.is_closed():
                await conn.close()
                logger.info("Connection closed")


async def main():
    logger.info("Starting email worker...")
    asyncio.create_task(recover_pending())
    await asyncio.gather(
        start_listener(),
        retry_pending(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Worker crashed: {e}")
        raise