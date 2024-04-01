from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.exceptions import HTTPException

from examples.schemas import Status
from users.auth import create_access_token, verify_token, pwd_context
from users.schemas import UserCreateSchema, UserListSchema, UserUpdateSchema, UserLoginSchema
from users.models import User

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post("/register", response_model=UserListSchema)
async def register(data: UserCreateSchema):
    user = User(username=data.username, email=data.email, password=pwd_context.hash(data.password))
    await user.save()
    if user:
        return user
    else:
        raise HTTPException(status_code=400, detail="Failed to register user")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@users_router.post("/token")
async def login_for_access_token(form_data: UserLoginSchema):
    user = await User.get(username=form_data.username)
    if user and pwd_context.verify(form_data.password, user.password):
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@users_router.get("/protected-route")
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        return {"message": "You are authorized"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@users_router.get('/', response_model=List[UserListSchema])
async def get_users():
    return await User.all()


@users_router.get('/{user_id}', response_model=UserListSchema)
async def get_user(user_id: int):
    user_obj = await User.get(id=user_id)
    return user_obj


@users_router.put('/{user_id}', response_model=UserListSchema)
async def update_user(user_id: int, data: UserUpdateSchema):
    user = await User.filter(id=user_id).update(**data.model_dump())
    print(user)
    return await User.get(id=user_id)


@users_router.delete('/{user_id}', response_model=UserListSchema)
async def delete_user(user_id: int):
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f'Example {user_id} not found')
    return Status(message=f'Example {user_id} deleted', details=None)
