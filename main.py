from fastapi import FastAPI, APIRouter
from tortoise.contrib.fastapi import register_tortoise

from example.router import example_model_router
from categories.router import category_router

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



