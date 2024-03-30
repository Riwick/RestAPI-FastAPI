import logging
from typing import List

from fastapi import APIRouter
from starlette.exceptions import HTTPException

from example.models import ExampleModel
from example.schemas import ListExamplePydantic, CreateExamplePydantic, Status

example_model_router = APIRouter(prefix='/examples', tags=['examples'])


@example_model_router.get('/', response_model=List[ListExamplePydantic])
async def get_examples():
    return await ExampleModel.all().select_related('category')


@example_model_router.get('/{example_id}', response_model=ListExamplePydantic)
async def get_example(example_id: int):
    example_obj = await ExampleModel.get(id=example_id).select_related('category')
    return example_obj


@example_model_router.post('/', response_model=ListExamplePydantic)
async def create_example(data: CreateExamplePydantic):
    example_obj = await ExampleModel.create(**data.model_dump())
    return example_obj


@example_model_router.put('/{example_id}', response_model=ListExamplePydantic)
async def update_example(example_id: int, data: CreateExamplePydantic):
    await ExampleModel.filter(id=example_id).update(**data.model_dump())
    return await ExampleModel.get(id=example_id).select_related('category')


@example_model_router.delete('/{example_id}', response_model=ListExamplePydantic)
async def delete_example(example_id: int):
    deleted_count = await ExampleModel.filter(id=example_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f'Example {example_id} not found')
    return Status(message=f'Example {example_id} deleted', details=None)
