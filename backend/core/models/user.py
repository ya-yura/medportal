from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, Column, String, Boolean, ForeignKey, Index

from .base import Base


class Role(Base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    permissions = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    hashed_password = Column(String(length=1024), nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey('Role.id'), nullable=False)

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    fathername = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String, nullable=True)

    # Явное создание индекса через SQLAlchemy
    __table_args__ = (
        Index('idx_users_email', 'email'),  # Явно создаем индекс на поле email
    )
