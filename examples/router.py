from typing import List

from fastapi import APIRouter, Query, Depends

from starlette import status
from starlette.exceptions import HTTPException

from examples.models import ExampleModel
from examples.schemas import ListExamplePydantic, CreateExamplePydantic, Status
from examples.cache import cache

from users.auth import verify_token
from users.models import User
from users.router import oauth2_scheme

example_model_router = APIRouter(prefix='/examples', tags=['examples'])


@example_model_router.get('/', response_model=List[ListExamplePydantic])
async def get_examples(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                       order_by: str = Query('id'),
                       title: str = Query(None), price: float = Query(None, ge=1),
                       category_id: int = Query(None, ge=1), example_id: int = Query(None, ge=1)):
    filters = {}
    if title:
        filters['title'] = title
    if price:
        filters['price'] = price
    if category_id:
        filters['category'] = category_id
    if example_id:
        filters['id'] = example_id
    if filters:
        examples = await ExampleModel.filter(**filters).offset(offset).limit(limit).all().order_by(order_by)
    else:
        examples = await ExampleModel.filter().offset(offset).limit(limit).all().order_by(order_by)
    return examples


@example_model_router.get('/{example_id}', response_model=ListExamplePydantic)
async def get_example(example_id: int):
    cached_item = await cache.get(f'example_{example_id}')
    if cached_item:
        return cached_item
    example_obj = await ExampleModel.filter(id=example_id).first().values()
    if example_obj:
        await cache.set(f'example_{example_id}', example_obj)
        return example_obj
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')


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
        example_obj = await ExampleModel.filter(id=example_id).update(**data.model_dump())
        if example_obj:
            example_obj = await ExampleModel.filter(id=example_id).first().values()
            await cache.set(f'example_{example_id}', example_obj)
            return example_obj
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@example_model_router.delete('/{example_id}', response_model=Status)
async def delete_example(example_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        cached_example = cache.get(f'example_{example_id}')
        if cached_example:
            cache.delete(f'example_{example_id}')
        deleted_count = await ExampleModel.filter(id=example_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')
        return Status(message=f'Example {example_id} deleted', details=None)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
