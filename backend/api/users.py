
from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from core.models.user import User
from core.logger import logger
from auth.schemas import UserRead, UserUpdate
from auth.manager import get_user_manager
from auth.auth import auth_backend
from auth.mailer import send_forgot_password_email
from core.connection import get_async_session

# from pydantic import validator


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password.decode()


router = APIRouter(tags=["Users"])


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user()


@router.get("/me")
# @measure_execution_time
async def get_current_user(
    current_user: UserRead = Depends(current_user),
    db: AsyncSession = Depends(get_async_session),
):
    query = await db.execute(
        select(
            User.id,
            User.email,
            User.name,
            User.surname,
            User.fathername,
            User.username,
            User.phone
        ).where(User.id == current_user.id)
    )
    result = query.mappings().first()
    return result


@router.get("/verify/{token}")
async def verify_user_token(
    token: str,
    current_user: UserRead = Depends(current_user),
    db: AsyncSession = Depends(get_async_session),
):
    query = await db.execute(
        select(User)
        .where(User.verification_token == token)
    )
    user = query.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Verification token is invalid or user not found."
        )

    if user.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to access this resource."
        )

    user.is_verified = True
    user.verification_token = ""
    await db.commit()
    return "User verified successfully."


'''@router.get("/get_by_email/{email}")
# @measure_execution_time
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(db_helper.session_getter),
    user_manager: UserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.get_by_email(email)
    except fastapi_exceptions.UserNotExists:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/get_by_email2/{email}")
# @measure_execution_time
async def get_user_by_email2(
    email: str,
    db: AsyncSession = Depends(db_helper.session_getter)
):
    query = await db.execute(select(User).where(User.email == email))
    user = query.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user'''


@router.put("/update_user")
async def update_user(
    user: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(current_user),
):
    query = await db.execute(select(User).where(User.id == current_user.id))
    user_db = query.scalars().first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found.")
    user_db.name = user.name
    user_db.surname = user.surname
    user_db.fathername = user.fathername
    user_db.username = user.username
    user_db.phone = user.phone
    await db.commit()
    logger.info(f"User {user_db.email} updated.")
    return user_db


@router.delete("/delete/{email}")
async def delete_user(
    email: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(current_user),
):
    user_db = await db.execute(select(User).where(User.email == email))
    user = user_db.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to access this resource."
        )
    await db.delete(user)
    await db.commit()
    logger.info(f"User {email} deleted.")
    return user


@router.post("/forgot_password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_async_session),
):
    query = await db.execute(select(User).where(User.email == email))
    user = query.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await send_forgot_password_email(user.name, user.email)
    logger.info(f"Email forgot_password sent to {email}")
    return {"message": "Email sent successfully."}


@router.post("/reset_password")
async def reset_password(
    new_password: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(current_user),
):
    query = await db.execute(select(User).where(User.id == current_user.id))
    user = query.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = hash_password(new_password)
    await db.commit()
    logger.info(f"User {user.email} password reset.")
    return {"message": "Password reset successfully."}
