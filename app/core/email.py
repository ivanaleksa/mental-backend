from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    # MAIL_TLS=settings.MAIL_TLS,
    # MAIL_SSL=settings.MAIL_SSL,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=True
)

fast_mail = FastMail(conf)

async def send_confirmation_email(email: str, code: str, action: str):
    subject = f"Подтверждение {action}"
    body = f"""
    <h2>Подтверждение {action}</h2>
    <p>Ваш код подтверждения: <strong>{code}</strong></p>
    <p>У вас есть <b>3 часа</b> для подтверждения аккаунта.</p>
    <p>Если вы не запрашивали это действие, проигнорируйте это письмо.</p>
    """
    
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html"
    )
    
    await fast_mail.send_message(message)
