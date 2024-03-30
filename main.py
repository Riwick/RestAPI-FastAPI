from fastapi import FastAPI, APIRouter

app = FastAPI(title='RestAPI-FastAPI')

main_router = APIRouter(prefix='/api/v1', tags=['api-v1'])


@main_router.get('/')
async def home_page():
    return 'Hello world!'


app.include_router(main_router)