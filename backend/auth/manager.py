import logging
from typing import Optional
import uuid
from fastapi import Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import (
    BaseUserManager, IntegerIDMixin, schemas, exceptions, models
    )

# from celery import Celery

from core.connection import User, get_user_db
from .mailer import send_verification_email, send_forgot_password_email
from .schemas import AuthForgotPassword


# Настройка логирования
logger = logging.getLogger("user_manager")
logger.setLevel(logging.INFO)  # Устанавливаем уровень логов
file_handler = logging.FileHandler("user_manager.log")
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


'''celery_app = Celery('tasks', broker='redis://localhost:6379/0')


@celery_app.task
def send_verification_email_celery(
    name: str, email: str, verification_token: str
):
    send_verification_email(name, email, verification_token)'''


SECRET = "secret"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verify_password_token_secret = SECRET

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
        # background_tasks: Optional[BackgroundTasks] = None
    ) -> models.UP:
        """
        Create a user in database.
        """

        try:
            await self.validate_password(user_create.password, user_create)

            existing_user = await self.user_db.get_by_email(user_create.email)
            if existing_user is not None:

                logger.exception(
                    f"User with email {user_create.email} already exists."
                )
                raise exceptions.UserAlreadyExists()

            user_dict = (
                user_create.create_update_dict()
                if safe
                else user_create.create_update_dict_superuser()
            )
            password = user_dict.pop("password")
            user_dict["hashed_password"] = self.password_helper.hash(password)
            user_dict["verification_token"] = str(uuid.uuid4())

            # Пытаемся отправить email перед созданием пользователя
            email_sent = await send_verification_email(
                user_dict["name"],
                user_dict["email"],
                user_dict["verification_token"]
            )

            if not email_sent:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to send verification email. Please try again or use a different email address."
                )

            created_user = await self.user_db.create(user_dict)
            logger.info(f"User {created_user.email} created successfully.")

            return created_user

        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists."
            )
        except HTTPException as he:
            # Пробрасываем HTTPException дальше
            raise he
        except Exception as e:
            logger.exception(
                f"Error creating user {user_create.email}: {str(e)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to create user. Please try again later."
            )

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
        # background_tasks: BackgroundTasks = None,
    ):
        try:
            await send_verification_email(
                user.name,
                user.email,
                user.verification_token)
            # background_tasks.add_task(
            #     send_verification_email,
            #     user.name,
            #     user.email,
            #     user.verification_token
            # )
            logger.info(f"Verification email sent to {user.email}.")

        except Exception as e:
            logger.exception(
                f"Failed to send verification email to {user.email}: {str(e)}"
            )

    async def on_after_request_verify(
        self,
        user: models.UP,
        token: str,
        request: Optional[Request] = None,
        db: AsyncSession = Depends(get_user_db),
    ) -> None:
        query = await db.execute(
            select(User.id)
            .where(User.verification_token == token)
        )
        user_id = query.first()
        if user_id is None:
            raise HTTPException(status_code=404)
        return  # pragma: no cover

    async def send_forgot_password(
            self,
            email: str,
            user: User,
            db: AsyncSession = Depends(get_user_db),
    ):
        query = await db.execute(
            select(User)
            .where(User.email == email)
        )
        user = query.first()
        try:
            user = await self.user_db.get_by_email(user.email)
            if user is None:
                raise exceptions.UserNotExists()

            # user.reset_password_token = str(uuid.uuid4())
            # await self.user_db.update(user)
            logger.info(f"Forgot password email sent to {user.email}.")

            await send_forgot_password_email(user.name, user.email)

        except Exception as e:
            logger.exception(
                f"Failed to send reset password email to {user.email}: {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail="Failed to send reset password email"
            )

    '''async def reset_password(
        self,
        token: str,
        new_password: str,
        db: AsyncSession = Depends(get_user_db),
    ):
        try:
            user = await self.user_db.get_by_reset_password_token(token)
            if user is None:
                raise exceptions.UserNotExists()'''


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
