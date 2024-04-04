import datetime

from pydantic import BaseModel, EmailStr, validator


class UserCreateSchema(BaseModel):
    """Схема создания пользователя"""
    username: str
    password: str
    email: EmailStr


class UserLoginSchema(BaseModel):
    """Схема, по которой пользователь заходит в аккаунт"""
    username: str
    password: str


class UserListSchema(BaseModel):
    """Схема по которой пользователь выводится другим пользователям или при удалении/обновлении"""
    id: int
    username: str
    date_joined: datetime.datetime | str


class UserProfileSchema(BaseModel):
    """Схема по которой пользователю выводиться информация о себе"""
    id: int
    username: str
    date_joined: datetime.datetime | str
    is_active: bool
    is_superuser: bool
    email: EmailStr


class UserUpdateSchema(BaseModel):
    """Схема по которой происходит обновление пользователя"""
    username: str

