from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel, field_validator, ConfigDict

from core.validators import SchemaValidator


class User(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    name: str
    surname: str
    fathername: str
    phone: str

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    name: str
    surname: str
    fathername: str
    phone_number: str
    role: str
    karma: int = 0
    level: int = 1
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserData(BaseModel):
    info: Optional[dict] = None


class UserRead(schemas.BaseUser):
    id: int
    email: str
    username: str
    name: str
    surname: str
    fathername: str
    phone_number: str
    role: str
    karma: int
    level: int


class UserUpdate(UserRead):
    pass


class AuthForgotPassword(BaseModel):
    email: str

    @field_validator("email")
    def validate_email(cls, email):
        return SchemaValidator.validate_email(email)

    model_config = ConfigDict(from_attributes=True)
