import logging

import uvicorn
from fastapi import FastAPI, APIRouter
from tortoise.contrib.fastapi import register_tortoise

from examples.router import example_model_router
from categories.router import category_router
from users.router import users_router


"""Конфигурация логгера для TortoiseORM для вывода в консоль запросов в БД"""

fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
sh = logging.StreamHandler()
sh.setFormatter(fmt)

logger_tortoise = logging.getLogger("tortoise.db_client")
logger_tortoise.setLevel(logging.DEBUG)
logger_tortoise.addHandler(sh)


app = FastAPI(title='RestAPI-FastAPI')

"""Подключение роутеров"""

main_router = APIRouter(prefix='/api/v1', tags=[])

main_router.include_router(example_model_router)
main_router.include_router(category_router)
main_router.include_router(users_router)


@main_router.get('/')
async def home_page():
    """Тестовая функция"""
    return 'Hello world!'


"""Включение всех роутеров в приложение"""
app.include_router(main_router)


"""Конфигурация TortoiseORM для postgresql"""
register_tortoise(
    app=app,
    config={
        'connections': {
            'default': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': 'localhost',
                    'port': '10000',
                    'user': 'postgres',
                    'password': 'postgres',
                    'database': 'postgres',
                }
            },
            'default': 'postgres://postgres:postgres@localhost:10001/postgres'
        },
        'apps': {
            'models': {
                'models': ['examples.models', 'categories.models', 'users.models'],
                'default_connection': 'default',
            }
        }
    },
    generate_schemas=True,
    add_exception_handlers=True,
)

"""Точка запуска приложения"""
if __name__ == '__main__':
    uvicorn.run(app='main:app', host='localhost', port=10000, reload=True)
