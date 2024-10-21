import datetime
from sqlalchemy import (Column, Integer, String, ForeignKey, Float, DateTime,
                        Text, Date, Boolean, Enum, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Информация о пользователях системы, как пациенты и медицинские работники
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    registration_date = Column(DateTime)
    name = Column(String, nullable=False)  # Имя
    sirname = Column(String, nullable=False)  # Фамилия
    fathername = Column(String, nullable=False)  # Отчество
    role = Column(String)  # Роль пользователя (пациент, врач, администратор)
    karma = Column(Integer, default=0)  # Карма пользователя
    level = Column(Integer, default=1)  # Уровень пользователя

    # Связи
    achievements = relationship("Achievement", secondary="user_achievements", back_populates="users")
    reviews = relationship("Review", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")


# Информация о клиниках, где работают врачи
class Clinic(Base):
    __tablename__ = 'clinics'

    clinic_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    phone_number = Column(String)
    website = Column(String)


# Таблица образовательных учреждений
class EducationalInstitution(Base):
    __tablename__ = 'educational_institutions'

    institution_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    accreditation = Column(String)


# Таблица квалификаций
class Qualification(Base):
    __tablename__ = 'qualifications'

    qualification_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)


# Таблица специальностей
class Specialization(Base):
    __tablename__ = 'specializations'

    specialization_id = Column(Integer, primary_key=True, index=True)
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
    user_id = Column(Integer, ForeignKey('users.user_id'))
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

    workplaces = relationship("Workplace", back_populates="doctor")
    education_id = Column(Integer, ForeignKey('educational_institutions.institution_id'))
    qualification_id = Column(Integer, ForeignKey('qualifications.qualification_id'))
    specialization_id = Column(Integer, ForeignKey('specializations.specialization_id'))

    education = relationship("EducationalInstitution")
    qualification = relationship("Qualification")
    specialization = relationship("Specialization")
    reviews = relationship("Review", back_populates="doctor")


# Таблица для хранения информации о местах работы врача
class Workplace(Base):
    __tablename__ = 'workplaces'
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'))
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

    users = relationship("User", secondary="user_achievements", back_populates="achievements")


# Таблица для связи пользователей и их достижений
class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    achieved_at = Column(DateTime, default=datetime.datetime.utcnow)


# Таблица активности пользователей на платформе
class UserActivity(Base):
    __tablename__ = 'user_activities'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    activity_type = Column(Enum('visit', 'review', 'like', 'comment', 'referral', name="activity_types"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(Text)

    user = relationship("User", back_populates="activities")


# Таблица лайков отзывов
class ReviewLike(Base):
    __tablename__ = 'review_likes'
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    review = relationship("Review", back_populates="likes")
    user = relationship("User")


# Таблица для реферальной программы
class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    referred_user_id = Column(Integer, ForeignKey('users.user_id'))
    bonus_awarded = Column(Boolean, default=False)

    referred_user = relationship("User", foreign_keys=[referred_user_id])
    referrer = relationship("User", foreign_keys=[user_id])


# Записи на приём
class Appointment(Base):
    __tablename__ = 'appointments'

    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'))
    appointment_date = Column(DateTime)
    status = Column(String)














'''


# Медицинские данные пользователей, такие как температура, давление и пр.
class MedicalInfo(Base):
    __tablename__ = 'medical_info'
    
    info_id = Column(Integer, primary_key=True, index=True)
    # Идентификатор пользователя, к которому относятся данные
    user_id = Column(Integer, ForeignKey('users.user_id'))
    # Температура тела
    temperature = Column(Float)
    # Кровяное давление (например, "120/80")
    blood_pressure = Column(String)
    # Уровень сахара в крови
    blood_sugar = Column(Float)
    # Дата записи медицинской информации
    date_recorded = Column(DateTime)


# Таблица симптомов
class Symptom(Base):
    __tablename__ = 'symptoms'
    
    symptom_id = Column(Integer, primary_key=True, index=True)
    # Название
    name = Column(String)
    # Описание
    description = Column(Text)


# Болезни
class Disease(Base):
    __tablename__ = 'diseases'
    
    disease_id = Column(Integer, primary_key=True, index=True)
    # Название
    name = Column(String)
    # Описание заболевания
    description = Column(Text)


# Модель для таблицы активных ингредиентов
class ActiveIngredient(Base):
    __tablename__ = 'active_ingredients'
    
    ingredient_id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор активного ингредиента (первичный ключ)
    name = Column(String)  # Название активного ингредиента
    description = Column(Text)  # Описание активного ингредиента (опционально)

    medications = relationship("Medication", back_populates="active_ingredient")  # Связь с моделью Medication


# Модель для таблицы показаний
class Indication(Base):
    __tablename__ = 'indications'
    
    indication_id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор показания (первичный ключ)
    description = Column(Text)  # Описание показания

    medications = relationship("MedicationIndication", back_populates="indication")  # Связь с моделью MedicationIndication


# Модель для таблицы побочных эффектов
class SideEffect(Base):
    __tablename__ = 'side_effects'
    
    side_effect_id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор побочного эффекта (первичный ключ)
    description = Column(Text)  # Описание побочного эффекта

    medications = relationship("MedicationSideEffect", back_populates="side_effect")  # Связь с моделью MedicationSideEffect


# Модель для связи между лекарствами и показаниями
class MedicationIndication(Base):
    __tablename__ = 'medication_indications'
    
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор записи (первичный ключ)
    medication_id = Column(Integer, ForeignKey('medications.medication_id'))  # Идентификатор лекарства
    indication_id = Column(Integer, ForeignKey('indications.indication_id'))  # Идентификатор показания

    medication = relationship("Medication", back_populates="indications")  # Связь с моделью Medication
    indication = relationship("Indication", back_populates="medications")  # Связь с моделью Indication


# Модель для связи между лекарствами и побочными эффектами
class MedicationSideEffect(Base):
    __tablename__ = 'medication_side_effects'
    
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор записи (первичный ключ)
    medication_id = Column(Integer, ForeignKey('medications.medication_id'))  # Идентификатор лекарства
    side_effect_id = Column(Integer, ForeignKey('side_effects.side_effect_id'))  # Идентификатор побочного эффекта

    medication = relationship("Medication", back_populates="side_effects")  # Связь с моделью Medication
    side_effect = relationship("SideEffect", back_populates="medications")  # Связь с моделью SideEffect


# Модель для таблицы лекарств
class Medication(Base):
    __tablename__ = 'medications'
    
    medication_id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор лекарства (первичный ключ)
    name = Column(String)  # Название лекарства
    active_ingredient_id = Column(Integer, ForeignKey('active_ingredients.ingredient_id'))  # Идентификатор активного ингредиента (внешний ключ)

    active_ingredient = relationship("ActiveIngredient", back_populates="medications")  # Связь с моделью ActiveIngredient
    indications = relationship("MedicationIndication", back_populates="medication")  # Связь с моделью MedicationIndication
    side_effects = relationship("MedicationSideEffect", back_populates="medication")  # Связь с моделью MedicationSideEffect


# История здоровья
class HealthHistory(Base):
    __tablename__ = 'health_history'
    
    history_id = Column(Integer, primary_key=True, index=True)
    # Идентификатор пользователя, чья история здоровья записана
    user_id = Column(Integer, ForeignKey('users.user_id'))
    # Дата записи
    date = Column(DateTime)
    # Симптомы, наблюдавшиеся в этот период
    symptoms = Column(Text)
    # Диагноз, поставленный пользователю
    diagnosis = Column(Text)
    # Лечение, назначенное пользователю
    treatment = Column(Text)

    user = relationship('User', back_populates='health_histories')


    
'''