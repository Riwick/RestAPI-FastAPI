import datetime

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserListSchema(BaseModel):
    id: int
    username: str
    date_joined: datetime.datetime
    is_active: bool
    is_superuser: bool
    email: EmailStr


class UserUpdateSchema(BaseModel):
    username: str

