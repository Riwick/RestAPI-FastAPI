import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


"""Файл с созданием и валидации JWT-токенов"""


SECRET_KEY = "your-secret-key"  # Секретный ключ для создания токенов
ALGORITHM = "HS256"  # Алгоритм шифровки токенов
ACCESS_TOKEN_EXPIRE_MINUTES = 360  # Время жизни токенов


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_token(token: str):
    """Эта функция отвечает за валидацию токенов"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """Эта функция отвечает за создание токенов"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
