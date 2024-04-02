import datetime

from pydantic import BaseModel, EmailStr, validator


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
    date_joined: datetime.datetime | str


class UserProfileSchema(BaseModel):
    id: int
    username: str
    date_joined: datetime.datetime | str
    is_active: bool
    is_superuser: bool
    email: EmailStr


class UserUpdateSchema(BaseModel):
    username: str

