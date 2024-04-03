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

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post("/register", response_model=UserListSchema)
async def register(data: UserCreateSchema, background_tasks: BackgroundTasks):
    try:
        user = User(username=data.username, email=data.email, password=pwd_context.hash(data.password),
                    confirm_code=hashlib.sha256(data.email.encode()).hexdigest()[:6])
        await user.save()
    except:
        HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                      detail="User with this username or email has already registered")
        raise
    background_tasks.add_task(send_email, data.email, user.confirm_code)
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to register user")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@users_router.post('/confirm-email/{confirm_code}', response_model=UserListSchema)
async def confirm_email(confirm_code: str):
    user = await User.get(confirm_code=confirm_code)
    if user:
        user.confirmed = True
        await user.save()
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found or confirmation code is invalid')


@users_router.post("/login")
async def login_for_access_token(form_data: UserLoginSchema):
    try:
        user = await User.get(username=form_data.username)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User does not exists")
    if user and pwd_context.verify(form_data.password, user.password):
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Incorrect username or password")


@users_router.get('/me', response_model=UserProfileSchema)
async def get_profile(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        cached_user = await cache.get(f'user_profile_{payload.get('sub')}')
        if cached_user:
            return cached_user
        user_obj = await User.filter(username=payload.get('sub')).first().values()
        await cache.set(f'user_profile_{payload.get('sub')}', user_obj)
        return user_obj
    else:
        raise HTTPException(status_code=status.HTTP_404_UNAUTHORIZED, detail="Invalid token")


@users_router.get('/', response_model=List[UserListSchema])
async def get_users(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                    order_by: str = Query('id'),
                    username: str = Query(None), user_id: int = Query(None)):
    filters = {}
    if username:
        filters['username'] = username
    if user_id:
        filters['id'] = user_id

    if filters:
        return await User.filter(**filters).offset(offset).limit(limit).all().order_by(order_by)

    return await User.filter().offset(offset).limit(limit).all().order_by(order_by)


@users_router.get('/{user_id}', response_model=UserListSchema)
async def get_user(user_id: int):
    cached_user = await cache.get(f'user_{user_id}')
    if cached_user:
        return cached_user
    user_obj = await User.filter(id=user_id).first().values()
    if user_obj:
        await cache.set(f'user_{user_id}', user_obj)
        return user_obj
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')


@users_router.put('/{user_id}', response_model=UserListSchema)
async def update_user(user_id: int, data: UserUpdateSchema, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    query_user = await User.filter(username=payload.get('sub')).first().only('is_superuser')
    user_obj = await User.get(id=user_id).only('username')
    if query_user.is_superuser or user_obj.username == payload.get('sub'):
        updated_count = await User.filter(id=user_id).update(**data.model_dump())
        if updated_count:
            updated_user = await User.get(id=user_id).values()
            await cache.set(f'user_{user_id}', updated_user)
            return updated_user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@users_router.delete('/{user_id}', response_model=Status)
async def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub')).only('is_superuser')
    if user.is_superuser:
        deleted_count = await User.filter(id=user_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')
        await cache.delete(f'user_{user_id}')
        return Status(message=f'User {user_id} deleted')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
