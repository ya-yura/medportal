from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    name: str
    surname: str
    fathername: str
    email: str
    phone: str
    hashed_password: str
