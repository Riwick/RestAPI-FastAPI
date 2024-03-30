from typing import List

from fastapi import APIRouter

from example.models import ExampleModel, Category
from example.schemas import ListExamplePydantic, ListCategoryPydantic, CreateExamplePydantic, CreateCategoryPydantic

example_model_router = APIRouter(prefix='/examples', tags=['examples'])


@example_model_router.get('/', response_model=List[ListExamplePydantic])
async def get_example_models():
    return await ExampleModel.all()


@example_model_router.post('/', response_model=ListExamplePydantic)
async def create_example_model(data: CreateExamplePydantic):
    example_obj = await ExampleModel.create(**data.model_dump())
    return await example_obj


category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/', response_model=List[ListCategoryPydantic])
async def get_categories():
    return await Category.all()


@category_router.post('/', response_model=ListCategoryPydantic)
async def create_category(data: CreateCategoryPydantic):
    cat_obj = await Category.create(**data.model_dump())
    return await cat_obj
