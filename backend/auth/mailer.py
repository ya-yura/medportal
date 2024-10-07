import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

from core.config import settings


load_dotenv()

EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))


def send_email(subject: str, to_email: str, html_content: str):
    message = EmailMessage()
    message.add_alternative(html_content, subtype="html")
    message["Subject"] = subject
    message["From"] = EMAIL_USERNAME
    message["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, to_email, message.as_string())


def send_verification_email(username: str, email: str, token: str):

    html_content = f"""
    <html>
        <body>
            <p>Привет, {username}!</p>
            <p>Спасибо за регистрацию на нашем сайте. Пожалуйста, подтвердите ваш email, нажав на кнопку ниже:</p>
            <a href="http://127.0.0.1:8000/api/v1/users/verify/{token}">Подтвердить Email</a>
            <p>Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
            <br>
            <p>С наилучшими пожеланиями,<br>Команда ####</p>
        </body>
    </html>
    """
    send_email("Email verification", email, html_content)


def send_forgot_password_email(username: str, email: str):

    html_content = f"""
    <html>
        <body>
            <p>Здравствуйте, {username}!</p>
            <p>К сожалению, по соображениям безопасности мы не можем отправить вам ваш текущий пароль. Однако, вы можете сбросить его, перейдя по следующей ссылке:</p>
            <a href="http://127.0.0.1:8000/api/v1/users/reset_password">[Ссылка для сброса пароля]</a>
            <p>Эта ссылка будет активна в течение 60 минут.</p>
            <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.</p>
            <br>
            <p>С наилучшими пожеланиями,<br>Команда ####</p>
        </body>
    </html>
    """
    send_email("Email verification", email, html_content)
