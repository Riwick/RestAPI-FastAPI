import logging
import sys
from typing import List

from fastapi import APIRouter, Query, Depends
from starlette import status
from starlette.exceptions import HTTPException
from tortoise.expressions import Q

from examples.models import ExampleModel
from examples.schemas import ListExamplePydantic, CreateExamplePydantic, Status
from users.auth import verify_token
from users.models import User
from users.router import oauth2_scheme

example_model_router = APIRouter(prefix='/examples', tags=['examples'])


example_model_logger = logging.Logger(name='example_logger')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
example_model_logger.addHandler(handler)
example_model_logger.setLevel(logging.DEBUG)


@example_model_router.get('/', response_model=List[ListExamplePydantic])
async def get_examples(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                       sort_by: str = Query('id')):
    return await ExampleModel.filter().offset(skip).limit(limit).all().order_by(sort_by)


@example_model_router.get('/{example_id}', response_model=ListExamplePydantic)
async def get_example(example_id: int):
    example_obj = await ExampleModel.get(id=example_id)
    return example_obj


@example_model_router.post('/', response_model=ListExamplePydantic)
async def create_example(data: CreateExamplePydantic, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        example_obj = await ExampleModel.create(**data.model_dump())
        return example_obj
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@example_model_router.put('/{example_id}', response_model=ListExamplePydantic)
async def update_example(example_id: int, data: CreateExamplePydantic, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        await ExampleModel.filter(id=example_id).update(**data.model_dump())
        return ExampleModel.get(id=example_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@example_model_router.delete('/{example_id}', response_model=Status)
async def delete_example(example_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        deleted_count = await ExampleModel.filter(id=example_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')
        return Status(message=f'Example {example_id} deleted', details=None)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
