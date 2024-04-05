from typing import List

from fastapi import APIRouter, Query, Depends
from starlette import status
from starlette.exceptions import HTTPException

from categories.models import Category
from categories.schemas import ListCategoryPydantic, CreateCategoryPydantic
from categories.cache import cache

from examples.schemas import Status
from users.auth import verify_token
from users.models import User
from users.router import oauth2_scheme


"""Инициализация роутера"""
category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/', response_model=List[ListCategoryPydantic])
async def get_categories(offset: int = Query(0), limit: int = Query(10),
                         order_by: str = Query('id'),
                         title: str = Query(None), cat_id: int = Query(None)):

    """Эта функция выводит все категории по 10 штук(можно задать своё значение, изменив limit)
        в формате:
        [
            {
                "id": 0,
                "title": "string"
            }
        ]
        Она поддерживает пагинацию через offset и limit, сортировку через order_by(по умолчанию стоит сортировка по id)
        и фильтры. Они идут после order_by в параметрах функции и представляют собой query-запросы.
        В случае если нет ни одного объекта, выводится пустой список []"""

    cached_categories = await cache.get('categories')  # Пытаемся взять данные из кеша
    if cached_categories:
        return cached_categories

    filters = {}
    if title:
        filters['title'] = title
    if cat_id:
        filters['id'] = cat_id

    if filters:
        """Получение результата с фильтрами через распаковку словаря **filters"""
        categories = await Category.filter(**filters).offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('categories', categories)  # Запись результата в кеш

    else:
        """Получение результата без фильтров"""
        categories = await Category.filter().offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('categories', categories)  # Запись результата в кеш

    return categories


@category_router.get('/{category_id}', response_model=ListCategoryPydantic)
async def get_category(category_id: int):

    """Эта функция отвечает за получение категории по id и выводит её в формате:
        {
            "id": 0,
            "title": "string"
        }
        Если категория не существует, пробрасывается ошибка 404"""

    cached_obj = await cache.get(f'category_{category_id}')  # Попытка получения кеша
    if cached_obj:
        return cached_obj  # Если кеш есть, то возвращаем его

    category_obj = await Category.filter(id=category_id).first().values()  # Получение объекта
    if category_obj:
        """В случае если категория найдена"""
        if not cached_obj:
            await cache.set(f'category_{category_id}', category_obj)  # Сохранение в кеш, если его нету
        return category_obj
    else:
        """В случае если категория не найдена пробрасывается 404 ошибка"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')


@category_router.post('/', response_model=ListCategoryPydantic)
async def create_category(data: CreateCategoryPydantic, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за создание категории. Её могут пользоваться только супер юзеры, в противном
        случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через JWT-токен и
        его параметр sub, в котором содержится username пользователя.
        После создания объекта, он выводится в формате:
        {
            "id": 0,
            "title": "string"
        }
        Данные для создания отправляются в теле запроса и валидируются через pydantic"""

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))  # Получаем пользователя из БД через токен
    if user.is_superuser:

        cat_obj = await Category.create(**data.model_dump())  # Создаём объект
        await cache.delete('categories')   # Удаляем кеш, который создавали в функции get_categories для его обновления
        return cat_obj
    else:
        """Если пользователь не является супер юзером, то пробрасывается ошибка 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@category_router.put('/{category_id}', response_model=ListCategoryPydantic)
async def update_category(category_id: int, data: CreateCategoryPydantic, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за обновление категории по ее id. Использовать функцию могут только
        супер юзеры, в противном случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через
        JWT-токен и его параметр sub, в котором содержится username пользователя.
        После обновления выводиться обновленные объект в формате:
        {
            "id": 0,
            "title": "string"
        }
        Данные для обновления валидируются через pydantic """

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))  # Получаем пользователя из БД через токен
    if user.is_superuser:

        cat_obj = await Category.filter(id=category_id).update(**data.model_dump())  # Пытаемся обновить объект
        if cat_obj:  # int
            """Если объект обновлен, то мы берем его из БД, сохраняем в кеш и отдаем пользователю"""
            cat_obj = await Category.filter(id=category_id).first().values()

            cached_obj = await cache.get(f'category_{category_id}')  # Получаем кеш и удаляем его, если он есть
            if cached_obj:
                await cache.delete(f'category_{category_id}')
            await cache.delete('categories')  # Удаляем кеш, который создавали в функции get_categories для его
            # обновления

            """Если объект был обновлен, то возвращаем ответ"""
            return cat_obj
        else:
            """Если объект не был обновлен, то пробрасываем ошибку 404"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Category {category_id} not found')
    else:
        """Если пользователь не является супер юзером, то пробрасываем ошибку 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@category_router.delete('/{category_id}', response_model=Status)
async def delete_category(category_id: int, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за удаление категории по ее id. Использовать функцию могут только
        супер юзеры, в противном случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через
        JWT-токен и его параметр sub, в котором содержится username пользователя.
        После успешного удаления возвращается ответ в формате:
        {
            "status_code": 200,
            "message": "string",
            "details": "string"
        }
        """

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))   # Получаем юзера из БД
    if user.is_superuser:

        deleted_cat = await Category.filter(id=category_id).delete()
        if not deleted_cat:
            """Если объект не был удален, то пробрасываем ошибку 404"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Category {category_id} not found')

        cached_example = cache.get(f'category_{category_id}')  # Получаем кеш и удаляем его, если он есть
        if cached_example:
            await cache.delete(f'category_{category_id}')
        await cache.delete('categories')  # Удаляем кеш, который создавали в функции get_categories для его обновления

        """Если объект был удален, то возвращаем ответ"""
        return Status(status_code=200, message=f'Category {category_id} deleted')
    else:
        """Если пользователь не является супер юзером, то пробрасываем ошибку 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
