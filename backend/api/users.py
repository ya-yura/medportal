
from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from core.models.db_model import (User, Doctor, EducationalInstitution,
                                  Qualification, Specialization,
                                  Achievement, UserActivity, UserAchievement,
                                  Appointment, Clinic)
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
    result = {}
    query = await db.execute(
        select(
            User.id,
            User.email,
            User.name,
            User.surname,
            User.fathername,
            User.username,
            User.phone_number,
            User.role,
        ).where(User.id == current_user.id)
    )
    user = query.mappings().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    else:
        result = dict(user)

    if user['role'] == 'doctor':
        query = await db.execute(
            select(
                Doctor.id,
                EducationalInstitution.name.label("education"),
                Qualification.name.label("qualification"),
                Specialization.name.label("specialization"),
                Doctor.photo_url,
            )
            .select_from(Doctor)
            .join(
                EducationalInstitution,
                Doctor.education_id == EducationalInstitution.id
            )
            .join(Qualification, Doctor.qualification_id == Qualification.id)
            .join(
                Specialization, Doctor.specialization_id == Specialization.id
            )
            .where(Doctor.user_id == current_user.id)
        )
        doctor_data = query.mappings().first()

        if doctor_data:
            # Добавляем данные доктора к данным пользователя
            result['doctor_info'] = {
                'doctor_id': doctor_data['id'],
                'education': doctor_data['education'],
                'qualification': doctor_data['qualification'],
                'specialization': doctor_data['specialization'],
                'photo_url': doctor_data['photo_url']
            }
    elif user['role'] == 'patient':
        query = await db.execute(
            select(
                Achievement.title.label("achievement"),
                UserAchievement.achieved_at.label("achievement_date"),
                UserActivity.activity_type.label("activity_type"),
            )
            .select_from(User)
            .join(UserAchievement, User.id == UserAchievement.user_id)
            .join(
                Achievement, UserAchievement.achievement_id == Achievement.id
            )
            .join(UserActivity, User.id == UserActivity.user_id)
            .where(User.id == current_user.id)
        )
        user_activity_data = query.mappings().first()

        appointments_query = await db.execute(
            select(
                Appointment.id.label("appointment_id"),
                Appointment.appointment_date.label("appointment_date"),
                Appointment.clinic_id.label("clinic_id"),
                Appointment.doctor_id.label("doctor_id"),
                Appointment.status.label("status"),
                # Данные клиники
                Clinic.name.label("clinic_name"),
                Clinic.address.label("clinic_address"),
                # Данные доктора
                User.name.label("doctor_name"),
                User.surname.label("doctor_surname"),
                User.fathername.label("doctor_fathername"),
                Specialization.name.label("specialization")
            )
            .select_from(Appointment)
            .join(Clinic, Appointment.clinic_id == Clinic.id)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .join(User, Doctor.user_id == User.id)
            .join(
                Specialization, Doctor.specialization_id == Specialization.id
            )
            .where(Appointment.user_id == current_user.id)
        )
        appointments_data = appointments_query.mappings().all()

        if user_activity_data:
            result['user_data'] = {
                'achievement': user_activity_data['achievement'],
                'achievement_date': user_activity_data['achievement_date'],
                'activity_type': user_activity_data['activity_type'],
            }

        if appointments_data:
            result['appointments'] = [
                {
                    'appointment_id': appointment['appointment_id'],
                    'appointment_date': appointment['appointment_date'],
                    'clinic': {
                        'id': appointment['clinic_id'],
                        'name': appointment['clinic_name'],
                        'address': appointment['clinic_address']
                        },
                    'doctor': {
                        'id': appointment['doctor_id'],
                        'name': appointment['doctor_name'],
                        'surname': appointment['doctor_surname'],
                        'fathername': appointment['doctor_fathername'],
                        'specialization': appointment['specialization']
                    },
                    'status': appointment['status'],
                }
                for appointment in appointments_data
            ]
    # else:
    #     # TODO дописать администратора

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
