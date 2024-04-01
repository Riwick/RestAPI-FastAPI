import logging
import sys
from typing import List

from fastapi import APIRouter, Query, Depends
from starlette.exceptions import HTTPException

from examples.models import ExampleModel
from examples.schemas import ListExamplePydantic, CreateExamplePydantic, Status

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
async def get_examples(skip: int = Query(0), limit: int = Query(10)):
    return await ExampleModel.filter().offset(skip).limit(limit).all()


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
    return ExampleModel.get(id=example_id).select_related('category')


@example_model_router.delete('/{example_id}', response_model=ListExamplePydantic)
async def delete_example(example_id: int):
    deleted_count = await ExampleModel.filter(id=example_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f'Example {example_id} not found')
    return Status(message=f'Example {example_id} deleted', details=None)

