import logging
import sys

import uvicorn
from fastapi import FastAPI, APIRouter
from tortoise.contrib.fastapi import register_tortoise

from example.router import example_model_router
from categories.router import category_router

fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)

# will print debug sql
logger_db_client = logging.getLogger("tortoise.db_client")
logger_db_client.setLevel(logging.DEBUG)
logger_db_client.addHandler(sh)

logger_tortoise = logging.getLogger("tortoise")
logger_tortoise.setLevel(logging.DEBUG)
logger_tortoise.addHandler(sh)


app = FastAPI(title='RestAPI-FastAPI')

main_router = APIRouter(prefix='/api/v1', tags=[])

main_router.include_router(example_model_router)
main_router.include_router(category_router)


@main_router.get('/')
async def home_page():
    return 'Hello world!'


app.include_router(main_router)

register_tortoise(
    app=app,
    db_url='postgres://postgres:postgres@localhost:10001/postgres',
    modules={'models': ['example.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='localhost', port=10000, reload=True)

