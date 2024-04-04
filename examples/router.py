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


"""Инициализация роутера"""
example_model_router = APIRouter(prefix='/examples', tags=['examples'])


@example_model_router.get('/', response_model=List[ListExamplePydantic])
async def get_examples(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1),
                       order_by: str = Query('id'),
                       title: str = Query(None), price: float = Query(None, ge=1),
                       category_id: int = Query(None, ge=1), example_id: int = Query(None, ge=1)):

    """Эта функция выводит все доступные объекты класса Example по 10 штук(можно задать своё значение, изменив limit)
    в формате:
    [
        {
            "id": 0,
            "title": "string",
            "age": 0,
            "price": 0,
            "description": "string",
            "category_id": 0
        }
    ]
    Она поддерживает пагинацию через offset и limit, сортировку через order_by(по умолчанию стоит сортировка по id)
    и фильтры. Они идут после order_by в параметрах функции и представляют собой query-запросы.
    В случае если нет ни одного объекта, выводится пустой список []"""

    cached_examples = await cache.get('examples')  # Пытаемся взять данные из кеша
    if cached_examples:
        return cached_examples

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
        """Получение результата с фильтрами через распаковку словаря **filters"""

        examples = await ExampleModel.filter(**filters).offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('examples', examples)  # Запись в кеш с фильтрами

    else:
        """Получение результата с без фильтров"""
        examples = await ExampleModel.filter().offset(offset).limit(limit).all().order_by(order_by).values()
        await cache.set('examples', examples)  # Запись в кеш без фильтров

    return examples


@example_model_router.get('/{example_id}', response_model=ListExamplePydantic)
async def get_example(example_id: int):

    """Эта функция отвечает за получение объекта класса Example по id и выводит его в формате:
    {
        "id": 0,
        "title": "string",
        "age": 0,
        "price": 0,
        "description": "string",
        "category_id": 0
    }
    Если объект не существует, пробрасывается ошибка 404"""

    cached_item = await cache.get(f'example_{example_id}')  # Попытка получения кеша
    if cached_item:
        return cached_item

    example_obj = await ExampleModel.filter(id=example_id).first().values()  # Получение объекта
    if example_obj:
        if not cached_item:
            await cache.set(f'example_{example_id}', example_obj)  # Сохранение в кеш, если его нету
        return example_obj
    else:
        """В случае если объект не найден пробрасывается 404 ошибка"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')


@example_model_router.post('/', response_model=ListExamplePydantic)
async def create_example(data: CreateExamplePydantic, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за создание объекта класса Example. Её могут пользоваться только супер юзеры, в противном
    случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через JWT-токен и его параметр sub,
    в котором содержится username пользователя.
    После создания объекта, он выводится в формате:
    {
        "title": "string",
        "age": 0,
        "price": 1,
        "description": "string",
        "category_id": 0
    }
    Данные для создания отправляются в теле запроса и валидируются через pydantic"""

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))  # Получаем пользователя из БД через токен
    if user.is_superuser:

        example_obj = await ExampleModel.create(**data.model_dump())  # Создаём объект
        await cache.delete('examples')  # Удаляем кеш, который создавали в функции get_examples для его обновления
        return example_obj

    else:
        """Если пользователь не является супер юзером, то пробрасывается ошибка 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@example_model_router.put('/{example_id}', response_model=ListExamplePydantic)
async def update_example(example_id: int, data: CreateExamplePydantic, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за обновление объекта модели Example по его id. Использовать функцию могут только
    супер юзеры, в противном случае будет проброшена ошибка 403 Forbidden. Валидация пользователя происходит через
    JWT-токен и его параметр sub, в котором содержится username пользователя.
    После обновления выводиться обновленные объект в формате:
    {
        "title": "string",
        "age": 0,
        "price": 1,
        "description": "string",
        "category_id": 0
    }
    Данные для обновления валидируются через pydantic """

    payload = verify_token(token)
    user = await User.get(username=payload.get('sub'))  # Получаем пользователя из БД через токен
    if user.is_superuser:

        example_obj = await ExampleModel.filter(id=example_id).update(**data.model_dump())  # Пытаемся обновить объект
        if example_obj:  # int
            """Если объект обновлен, то мы берем его из БД, сохраняем в кеш и отдаем пользователю"""
            example_obj = await ExampleModel.filter(id=example_id).first().values()

            cached_example = cache.get(f'example_{example_id}')  # Получаем кеш и удаляем его, если он есть
            if cached_example:
                await cache.delete(f'example_{example_id}')  # Удаляем кеш самого объекта
            await cache.delete('examples')  # Удаляем кеш, который создавали в функции get_examples для его обновления

            return example_obj
        else:
            """Если объект не был обновлен, то пробрасываем ошибку 404"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')
    else:
        """Если пользователь не является супер юзером, то пробрасываем ошибку 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')


@example_model_router.delete('/{example_id}', response_model=Status)
async def delete_example(example_id: int, token: str = Depends(oauth2_scheme)):

    """Эта функция отвечает за удаление объекта модели Example по его id. Использовать функцию могут только
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
    user = await User.get(username=payload.get('sub'))  # Получаем юзера из БД
    if user.is_superuser:

        deleted_count = await ExampleModel.filter(id=example_id).delete()  # Пытаемся удалить объект
        if not deleted_count:
            """Если объект не был удален, то пробрасываем ошибку 404"""
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Example {example_id} not found')

        cached_example = cache.get(f'example_{example_id}')  # Получаем кеш и удаляем его, если он есть
        if cached_example:
            await cache.delete(f'example_{example_id}')  # Удаляем кеш самого объекта
        await cache.delete('examples')  # Удаляем кеш, который создавали в функции get_examples для его обновления

        """Если объект был удален, то возвращаем ответ"""
        return Status(message=f'Example {example_id} deleted')
    else:
        """Если пользователь не является супер юзером, то пробрасываем ошибку 403"""
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have not enough permissions')
