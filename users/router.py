import hashlib
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.exceptions import HTTPException

from examples.schemas import Status

from users.auth import create_access_token, verify_token, pwd_context
from users.schemas import UserCreateSchema, UserListSchema, UserUpdateSchema, UserLoginSchema, UserProfileSchema
from users.models import User
from users.send_email import send_email
from users.cache import cache

"""Инициализация роутера"""
users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post("/register", response_model=UserListSchema)
async def register(data: UserCreateSchema, background_tasks: BackgroundTasks):
    """Эта функция отвечает за регистрацию пользователя. Она проверяет, существует ли уже пользователь
    с введенными значениями. Данные для создания пользователя отправляются в теле запроса и валидируются
    через pydantic. После создания пользователя происходит отправка email на его почту через BackgroundTasks
    После успешного создания возвращается пользователь в формате:
    {
        "username": "string",
        "password": "string",
        "email": "user@example.com"
    }"""

    try:
        user = await User.create(username=data.username, email=data.email, password=pwd_context.hash(data.password),
                                 confirm_code=hashlib.sha256(data.email.encode())
                                 .hexdigest()[:6])  # попытка создания пользователя
    except:
        """Если такой пользователь уже зарегистрирован, то пробрасывается ошибка 422 UNPROCESSABLE_ENTITY """
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="User with this username or email has already registered")
    if user:
        """Если пользователь был успешно создан, то создается таска на отправку ему email и возвращаются его данные"""
        background_tasks.add_task(send_email, data.email, user.confirm_code)
        await cache.delete('users')
        return user
    else:
        """Если что-то пошло не так"""
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to register user")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@users_router.post('/confirm-email/{confirm_code}', response_model=UserListSchema)
async def confirm_email(confirm_code: str):
    """После отправки email пользователю необходимо ввести код в качестве query-параметра, чтобы подтвердить
    получения письма. В случае успешного запроса возвращаем пользователя в формате:
    {
        "id": 0,
        "username": "string",
        "date_joined": "2024-04-04T09:31:05.137Z"
    }"""

    user = await User.get(confirm_code=confirm_code)  # Пытаемся получить пользователя по его коду подтверждения
    if user:
        """Если мы получили пользователя"""
        user.confirmed = True
        await user.save()  # Изменяем значение поля confirmed на True и отдаем пользователя
        return user
    else:
        """Если срок действия токена вышел или он отдан некорректно, то пробрасываем 404 ошибку"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found or confirmation code is invalid')


@users_router.post("/login")
async def login_for_access_token(form_data: UserLoginSchema):
    """В этой функции происходит создание JWT-токенов и отправка их юзерам. Если введенные данные
    валидны(такой пользователь существует и пароли совпадают), то создается токен и отдается юзеру.
    В противном случае пробрасывается ошибка 404.
    В успешном случае юзеру отправляются данные в формате:
    {
        "access_token": "access_token",
        "token_type": "bearer"
    }
    Причем, если неправильное имя пользователя то выведется "User does not exists", а если
    пароль - "Incorrect username or password". И обе будут с 404 кодом """

    try:
        user = await User.get(username=form_data.username)  # Пытаемся получить юзера
    except:
        """Если неправильный username"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User does not exists")

    if user and pwd_context.verify(form_data.password, user.password):  # Валидация пароля
        access_token = create_access_token(data={"sub": user.username})  # Если успешно, то создаем токен
        return {"access_token": access_token, "token_type": "bearer"}  # Отправляем юзеру

    else:
        """Если неправильный пароль"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Incorrect username or password")


@users_router.get('/me', response_model=UserProfileSchema)
async def get_profile(token: str = Depends(oauth2_scheme)):
    """Эта функция отдаёт пользователю его данные. Валидация пользователя происходит через JWT-токен и
        его параметр sub, в котором содержится username пользователя. По нему и получаем данные из БДю
        В случае успеха данные отдаются в следующем виде:
        {
            "id": 0,
            "username": "string",
            "date_joined": "2024-04-04T09:48:29.201Z",
            "is_active": true,
            "is_superuser": true,
            "email": "user@example.com"
        }
        Если нам не удается найти пользователя по токену, то пробрасываем 404 ошибку"""

    payload = verify_token(token)  # Проверяем токен
    if payload:

        cached_user = await cache.get(f'user_profile_{payload.get('sub')}')  # Получаем юзера
        if cached_user:  # Пытаемся получить кеш. Если есть, то отдаём его
            return cached_user

        user_obj = await User.filter(username=payload.get('sub')).first().values()  # Пытаемся получить юзера
        if user_obj:
            """Если пользователь есть"""
            await cache.set(f'user_profile_{payload.get('sub')}', user_obj)  # Записываем кеш

            return user_obj
        else:
            """Если такого пользователя не существует"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    else:
        """Если токен не был предоставлен"""
        raise HTTPException(status_code=status.HTTP_404_UNAUTHORIZED, detail="Invalid token")


@users_router.get('/', response_model=List[UserListSchema])
async def get_users(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                    order_by: str = Query('id'),
                    username: str = Query(None), user_id: int = Query(None)):
    """Эта функция выводит всех пользователей по 10 штук(можно задать своё значение, изменив limit)
        в формате:
        [
            {
                "id": 0,
                "username": "string",
                "date_joined": "2024-04-04T10:07:23.991Z"
            }
        ]
        Она поддерживает пагинацию через offset и limit, сортировку через order_by(по умолчанию стоит сортировка по id)
        и фильтры. Они идут после order_by в параметрах функции и представляют собой query-запросы.
        В случае если нет ни одного объекта, выводится пустой список []"""

    cached_users = await cache.get('users')  # Пытаемся взять данные из кеша
    if cached_users:
        return cached_users

    filters = {}
    if username:
        filters['username'] = username
    if user_id:
        filters['id'] = user_id

    if filters:
        """Получение результата с фильтрами через распаковку словаря **filters"""
        users = await User.filter(**filters).offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('users', users)  # Запись результата в кеш
    else:
        """Получение результата без фильтров"""
        users = await User.filter().offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('users', users)  # Запись результата в кеш

    return users


@users_router.get('/{user_id}', response_model=UserListSchema)
async def get_user(user_id: int):
    """Эта функция отвечает за получение пользователя по id и выводит её в формате:
    {
        "id": 0,
        "title": "string"
    }
    Если пользователь не существует, пробрасывается ошибка 404"""

    cached_user = await cache.get(f'user_{user_id}')  # Попытка получения кеша
    if cached_user:
        return cached_user  # Если кеш есть, то возвращаем его

    user_obj = await User.filter(id=user_id).first().values()  # Получение пользователя
    if user_obj:
        """В случае если пользователь найден"""
        await cache.set(f'user_{user_id}', user_obj)  # Сохранение в кеш, если его нету
    else:
        """В случае если категория не найдена пробрасывается 404 ошибка"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')


@users_router.put('/{user_id}', response_model=UserListSchema)
async def update_user(user_id: int, data: UserUpdateSchema, token: str = Depends(oauth2_scheme)):
    """Эта функция отвечает за обновление пользователя по его id. Использовать функцию могут только
    супер юзеры, либо сам пользователь, которого обновляют, в противном случае будет проброшена ошибка 403 Forbidden.
    Если пользователь не найден, пробрасывается 404 ошибка. Если пользователя не удалось обновить, пробрасывается 422
    ошибка.
    Валидация пользователя происходит через JWT-токен и его параметр sub, в котором содержится username пользователя.
    После обновления выводиться обновленные объект в формате:
    {
        "id": 0,
        "username": "string",
        "date_joined": "2024-04-04T10:18:02.396Z"
    }
    Данные для обновления валидируются через pydantic"""

    payload = verify_token(token)  # Проверяем токен
    query_user = await (User.filter(username=payload.get('sub')).
                        first().only('is_superuser'))  # Получаем пользователя по токену
    user_obj = await User.filter(id=user_id).first().only('username')  # Получаем обновляемого пользователя

    if user_obj:
        if query_user.is_superuser or user_obj.username == payload.get('sub'):  # Проверка прав доступа
            updated_count = await user_obj.update_from_dict(**data.model_dump())

            if updated_count:
                updated_user = await User.get(id=user_id).values()  # Получаем обновленного пользователя

                cached_example = cache.get(f'user_{user_id}')  # Получаем кеш и удаляем его, если он есть
                if cached_example:
                    await cache.delete(f'user_{user_id}')  # Удаляем кеш самого объекта
                await cache.delete(f'profile_{updated_user.get('username')}')  # Удаляем кеш профиля

                """Если объект был обновлен, то возвращаем ответ"""
                return updated_user
            else:
                """Если не получилось обновить пользователя"""
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail='Your input data is invalid')
        else:
            """Если обновить пользователя пытается не супер юзер и не сам пользователь"""
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
    else:
        """Если пользователь не найден"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')


@users_router.delete('/{user_id}', response_model=Status)
async def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    """Эта функция отвечает за удаление пользователя по его id. Использовать функцию могут только
    супер юзеры, в противном случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через
    JWT-токен и его параметр sub, в котором содержится username пользователя.
    После успешного удаления возвращается ответ в формате:
    {
        "status_code": 200,
        "message": "string",
        "details": "string"
    }
    """

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub')).only('is_superuser')  # Получаем юзера из БД
    if user.is_superuser:

        deleted_count = await User.filter(id=user_id).delete()
        if not deleted_count:
            """Если удаляемый пользователь не был удален"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')

        cached_user = await cache.get(f'user_{user_id}')  # Получаем кеш и удаляем его, если он есть
        if cached_user:
            await cache.delete(f'user_{user_id}')
        await cache.delete('users')  # Удаляем кеш, который создавали в функции get_categories для его обновления

        """Если объект был удален, то возвращаем ответ"""
        return Status(message=f'User {user_id} deleted')
    else:
        """Если пользователь не является супер юзером"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
