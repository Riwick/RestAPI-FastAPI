import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from categories.models import Category
from examples.models import ExampleModel
from main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:10000/api/v1/") as c:
            yield c


@pytest.mark.anyio
async def test_get_example(client: AsyncClient):
    response = await client.get('examples/1')
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }


@pytest.mark.anyio
async def test_get_examples(client: AsyncClient):
    response = await client.get('examples/')
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 2,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 3,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 4,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 5,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 6,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 7,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 8,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        },
        {
            "id": 9,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        }
    ]


@pytest.mark.anyio
async def test_create_example(client: AsyncClient):
    get_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_jwt_token.status_code == 200
    jwt_token = get_jwt_token.json().get('access_token')
    jwt_type = get_jwt_token.json().get('token_type')
    example_data = {
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }
    response = await client.post('/examples/', json=example_data,
                                 headers={'Authorization': f'{jwt_type.capitalize()} {jwt_token}'})
    assert response.status_code == 200


@pytest.mark.anyio
async def test_update_example(client: AsyncClient):
    get_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_jwt_token.status_code == 200
    jwt_token = get_jwt_token.json().get('access_token')
    jwt_type = get_jwt_token.json().get('token_type')
    example_data = {
        "title": "Example 1",
        "age": 2,
        "price": 2,
        "description": "string 1",
        "category_id": 1
    }
    examples = await ExampleModel.filter().all()
    last_example_id = examples[-1].id
    response = await client.put(f'/examples/{last_example_id}', json=example_data,
                                headers={'Authorization': f'{jwt_type.capitalize()} {jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "id": last_example_id,
        "title": "Example 1",
        "age": 2,
        "price": 2,
        "description": "string 1",
        "category_id": 1
    }


@pytest.mark.anyio
async def test_delete_example(client: AsyncClient):
    get_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    examples = await ExampleModel.filter().all()
    last_example_id = examples[-1].id
    assert get_jwt_token.status_code == 200
    jwt_token = get_jwt_token.json().get('access_token')
    jwt_type = get_jwt_token.json().get('token_type')
    response = await client.delete(f'/examples/{last_example_id}',
                                   headers={'Authorization': f'{jwt_type.capitalize()} {jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": f"Example {last_example_id} deleted",
        "details": None
    }
