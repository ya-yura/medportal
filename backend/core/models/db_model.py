import datetime
from sqlalchemy import (Integer, Column, String, Boolean,
                        ForeignKey, DateTime, Text, Date, Enum)
from sqlalchemy.orm import relationship

from .base import Base


# Информация о пользователях системы, как пациенты и медицинские работники
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String(length=1024), nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    registration_date = Column(DateTime)
    name = Column(String, nullable=False)  # Имя
    surname = Column(String, nullable=False)  # Фамилия
    fathername = Column(String, nullable=False)  # Отчество
    role = Column(String)  # Роль пользователя (пациент, врач, администратор)
    karma = Column(Integer, default=0)  # Карма пользователя
    level = Column(Integer, default=1)  # Уровень пользователя

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String, nullable=True)

    # Связи
    achievements = relationship(
        "Achievement",
        secondary="user_achievements",
        back_populates="user"
    )
    reviews = relationship("Review", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")
    doctor = relationship("Doctor", back_populates="user")


# Информация о клиниках, где работают врачи
class Clinic(Base):
    __tablename__ = 'clinics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    phone_number = Column(String)
    website = Column(String)


# Таблица образовательных учреждений
class EducationalInstitution(Base):
    __tablename__ = 'educational_institutions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    accreditation = Column(String)


# Таблица квалификаций
class Qualification(Base):
    __tablename__ = 'qualifications'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)


# Таблица специальностей
class Specialization(Base):
    __tablename__ = 'specializations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)


# Таблица должностей врачей
class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)


# Таблица для оценки врача по различным параметрам
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)

    flagged_fake = Column(Boolean, default=False)
    moderation_needed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    feedback = Column(Text)

    # Оценка по каждому из параметров (значения -1, 0 или 1)
    professionalism = Column(Integer)           # Профессионализм
    effectiveness = Column(Integer)             # Эффективность лечения
    communication = Column(Integer)             # Коммуникабельность
    attentiveness = Column(Integer)             # Внимательность
    punctuality = Column(Integer)               # Пунктуальность
    responsibility = Column(Integer)            # Ответственность
    friendliness = Column(Integer)              # Доброжелательность
    diagnosis_accuracy = Column(Integer)        # Точность диагноза
    treatment_adequacy = Column(Integer)        # Назначение лечения
    informativeness = Column(Integer)           # Информативность
    supportiveness = Column(Integer)            # Отзывчивость
    clinic_cleanliness = Column(Integer)        # Чистота и комфортность клиники
    cost_adequacy = Column(Integer)             # Стоимость услуг
    hygiene = Column(Integer)                   # Аккуратность и гигиена
    diagnosis_speed = Column(Integer)           # Скорость постановки диагноза
    equipment_skill = Column(Integer)           # Умение работать с оборудованием
    knowledge_relevance = Column(Integer)       # Актуальность знаний
    appointment_organization = Column(Integer)  # Организация приёма
    teamwork = Column(Integer)                  # Умение работать в команде
    loyalty = Column(Integer)                   # Лояльность к пациенту
    feedback_willingness = Column(Integer)      # Обратная связь

    user = relationship("User", back_populates="reviews")
    doctor = relationship("Doctor", back_populates="reviews")
    likes = relationship("ReviewLike", back_populates="review")


# Модель врача с оценками по критериям
class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    photo_url = Column(String)

    # Внешний ключ на таблицу пользователей
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # Связь с таблицей пользователей
    user = relationship("User", back_populates="doctor")

    workplaces = relationship("Workplace", back_populates="doctor")
    education_id = Column(
        Integer,
        ForeignKey('educational_institutions.id'), nullable=False
    )
    qualification_id = Column(
        Integer,
        ForeignKey('qualifications.id'), nullable=False
    )
    specialization_id = Column(
        Integer,
        ForeignKey('specializations.id'), nullable=False
    )

    education = relationship("EducationalInstitution")
    qualification = relationship("Qualification")
    specialization = relationship("Specialization")
    reviews = relationship("Review", back_populates="doctor")


# Таблица для хранения информации о местах работы врача
class Workplace(Base):
    __tablename__ = 'workplaces'
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    position_id = Column(Integer, ForeignKey('positions.id'))
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)

    doctor = relationship("Doctor", back_populates="workplaces")
    clinic = relationship("Clinic")
    position = relationship("Position")


# Таблица достижений
class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    icon_url = Column(String)

    user = relationship(
        "User",
        secondary="user_achievements",
        back_populates="achievements"
    )


# Таблица для связи пользователей и их достижений
class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    achievement_id = Column(
        Integer,
        ForeignKey('achievements.id'), primary_key=True
    )
    achieved_at = Column(DateTime, default=datetime.datetime.utcnow)


# Таблица активности пользователей на платформе
class UserActivity(Base):
    __tablename__ = 'user_activities'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_type = Column(
        Enum(
            'visit',
            'review',
            'like',
            'comment',
            'referral',
            name="activity_types"
        )
    )
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text)

    user = relationship("User", back_populates="activities")


# Таблица лайков отзывов
class ReviewLike(Base):
    __tablename__ = 'review_likes'
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    review = relationship("Review", back_populates="likes")
    user = relationship("User")


# Таблица для реферальной программы
class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    referred_user_id = Column(Integer, ForeignKey('users.id'))
    bonus_awarded = Column(Boolean, default=False)

    referred_user = relationship("User", foreign_keys=[referred_user_id])
    referrer = relationship("User", foreign_keys=[user_id])


# Записи на приём
class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    appointment_date = Column(DateTime)
    status = Column(String)
