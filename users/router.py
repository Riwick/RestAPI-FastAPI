import hashlib
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.exceptions import HTTPException

from examples.schemas import Status
from users.auth import create_access_token, verify_token, pwd_context
from users.schemas import UserCreateSchema, UserListSchema, UserUpdateSchema, UserLoginSchema
from users.models import User
from users.send_email import send_email

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post("/register", response_model=UserListSchema)
async def register(data: UserCreateSchema, background_tasks: BackgroundTasks):
    user = User(username=data.username, email=data.email, password=pwd_context.hash(data.password),
                confirm_code=hashlib.sha256(data.email.encode()).hexdigest()[:6])
    await user.save()
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
    user = await User.get(username=form_data.username)
    if user and pwd_context.verify(form_data.password, user.password):
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@users_router.get('/me', response_model=UserListSchema)
async def get_profile(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        return await User.get(username=payload.get('sub'))
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@users_router.get('/', response_model=List[UserListSchema])
async def get_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    return await User.filter().offset(skip).limit(limit).all()


@users_router.get('/{user_id}', response_model=UserListSchema)
async def get_user(user_id: int):
    user_obj = await User.get(id=user_id)
    return user_obj


@users_router.put('/{user_id}', response_model=UserListSchema)
async def update_user(user_id: int, data: UserUpdateSchema, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user:
        await User.filter(id=user_id).update(**data.model_dump())
        return await User.get(id=user_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@users_router.delete('/{user_id}', response_model=Status)
async def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        deleted_count = await User.filter(id=user_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User {user_id} not found')
        return Status(message=f'User {user_id} deleted', details=None)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
