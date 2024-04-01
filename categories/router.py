from typing import List

from fastapi import APIRouter, Query, Depends
from starlette import status
from starlette.exceptions import HTTPException

from categories.models import Category
from categories.schemas import ListCategoryPydantic, CreateCategoryPydantic
from examples.schemas import Status
from users.auth import verify_token
from users.models import User
from users.router import oauth2_scheme

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/', response_model=List[ListCategoryPydantic])
async def get_categories(skip: int = Query(0), limit: int = Query(10),
                         order_by: str = Query('id'),
                         title: str = Query(None), cat_id: int = Query(None)):
    filters = {}
    if title:
        filters['title'] = title
    if cat_id:
        filters['id'] = cat_id

    if filters:
        return await Category.filter(**filters).offset(skip).limit(limit).all().order_by(order_by)

    return await Category.filter().offset(skip).limit(limit).all().order_by(order_by)


@category_router.get('/{category_id}', response_model=ListCategoryPydantic)
async def get_category(category_id: int):
    category_obj = await Category.get(id=category_id)
    return category_obj


@category_router.post('/', response_model=ListCategoryPydantic)
async def create_category(data: CreateCategoryPydantic, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        cat_obj = await Category.create(**data.model_dump())
        return cat_obj
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@category_router.put('/{category_id}', response_model=ListCategoryPydantic)
async def update_category(category_id: int, data: CreateCategoryPydantic, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        await Category.filter(id=category_id).update(**data.model_dump())
        return await Category.get(id=category_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@category_router.delete('/{category_id}', response_model=Status)
async def delete_category(category_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))
    if user.is_superuser:
        deleted_cat = await Category.filter(id=category_id).delete()
        if not deleted_cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Category {category_id} not found')
        return Status(status_code=200, message=f'Category {category_id} deleted', details=None)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
