import os
import re

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

from core.logger import logger


load_dotenv()


EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

conf = ConnectionConfig(
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD,
    MAIL_FROM=EMAIL_USERNAME,
    MAIL_PORT=SMTP_PORT,
    MAIL_SERVER=SMTP_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)


async def send_forgot_password_email(name: str, email: str):
    html_content = f"""
    <html>
        <body>
            <p>Здравствуйте, {name}!</p>
            <p>К сожалению, по соображениям безопасности мы не можем отправить вам ваш текущий пароль. Однако, вы можете сбросить его, перейдя по следующей ссылке:</p>
            <a href="http://127.0.0.1:8000/reset_password">[Ссылка для сброса пароля]</a>
            <p>Эта ссылка будет активна в течение 60 минут.</p>
            <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.</p>
            <br>
            <p>С наилучшими пожеланиями,<br>Команда ####</p>
        </body>
    </html>
    """

    message = MessageSchema(
            subject="Reset your password",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
    await fastmail.send_message(message)


async def send_verification_email(name: str, email: str, token: str):
    html_content = f"""
    <html>
        <body>
            <p>Привет, {name}!</p>
            <p>Спасибо за регистрацию на нашем сайте. Пожалуйста, подтвердите ваш email, нажав на кнопку ниже:</p>
            <a href="http://127.0.0.1:8000/api/v1/users/verify/{token}">Подтвердить Email</a>
            <p>Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
            <br>
            <p>С наилучшими пожеланиями,<br>Команда ####</p>
        </body>
    </html>
    """
    try:
        # Базовая проверка формата email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")

        # Более строгая проверка email
        validate_email(email)

        message = MessageSchema(
            subject="Verify your email",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        await fastmail.send_message(message)
        logger.info(f"Verification email sent successfully to {email}")
        return True
    except EmailNotValidError as e:
        logger.error(f"Invalid email address {email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False
