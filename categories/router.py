import logging
import sys
from typing import List

from fastapi import APIRouter, Query
from starlette.exceptions import HTTPException

from categories.models import Category
from categories.schemas import ListCategoryPydantic, CreateCategoryPydantic
from examples.schemas import Status

category_router = APIRouter(prefix='/categories', tags=['categories'])


category_logger = logging.Logger(name='example_logger')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
category_logger.addHandler(handler)
category_logger.setLevel(logging.DEBUG)


@category_router.get('/', response_model=List[ListCategoryPydantic])
async def get_categories(skip: int = Query(0), limit: int = Query(10)):
    return await Category.filter().offset(skip).limit(limit).all()


@category_router.get('/{category_id}', response_model=ListCategoryPydantic)
async def get_category(category_id: int):
    category_obj = await Category.get(id=category_id)
    return category_obj


@category_router.post('/', response_model=ListCategoryPydantic)
async def create_category(data: CreateCategoryPydantic):
    cat_obj = await Category.create(**data.model_dump())
    return cat_obj


@category_router.put('/{category_id}', response_model=ListCategoryPydantic)
async def update_category(category_id: int, data: CreateCategoryPydantic):
    await Category.filter(id=category_id).update(**data.model_dump())
    return await Category.get(id=category_id)


@category_router.delete('/{category_id}', response_model=ListCategoryPydantic)
async def delete_category(category_id: int):
    deleted_cat = await Category.filter(id=category_id).delete()
    if not deleted_cat:
        raise HTTPException(status_code=404, detail=f'Category {category_id} not found')
    return Status(status_code=200, message=f'Category {category_id} deleted', details=None)
