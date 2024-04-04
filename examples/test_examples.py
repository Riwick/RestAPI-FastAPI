import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from examples.models import ExampleModel
from main import app


"""Файл с тестами"""


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:10000/api/v1") as c:
            yield c


@pytest.mark.anyio
async def test_get_example(client: AsyncClient):
    response = await client.get('/examples/2')
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }
    fail_response = await client.get('/examples/1')
    assert fail_response.status_code == 404

    cached_response = await client.get('/examples/2')
    assert cached_response.status_code == 200
    assert cached_response.json() == {
        "id": 2,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }


@pytest.mark.anyio
async def test_get_examples(client: AsyncClient):
    response = await client.get('/examples/')
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 2,
            "title": "string",
            "age": 1,
            "price": 1,
            "description": "string",
            "category_id": 1
        },
        {
            "id": 5,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        },
        {
            "id": 7,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        },
        {
            "id": 8,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        }
    ]


@pytest.mark.anyio
async def test_filters(client: AsyncClient):
    filter_response = await client.get('/examples/?offset=0&limit=10&order_by=id&example_id=2')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 2,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }]
    filter_response = await client.get('/examples/?offset=0&limit=10&order_by=id&category_id=2')
    assert filter_response.status_code == 200
    assert filter_response.json() == []
    filter_response = await client.get('/examples/?offset=0&limit=10&order_by=id&price=1')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 2,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    },
    ]
    filter_response = await client.get('/examples/?offset=0&limit=10&order_by=id&title=string')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 2,
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    },
    ]


@pytest.mark.anyio
async def test_ordering(client: AsyncClient):
    filter_response = await client.get('/examples/?offset=0&limit=10&order_by=price')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 2,
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
            "id": 7,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        },
        {
            "id": 5,
            "title": "Example 1",
            "age": 2,
            "price": 2,
            "description": "string 1",
            "category_id": 1
        }]


@pytest.mark.anyio
async def test_create_example(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    example_data = {
        "title": "string",
        "age": 1,
        "price": 1,
        "description": "string",
        "category_id": 1
    }
    response = await client.post('/examples/', json=example_data,
                                 headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')
    fail_response = await client.post('/examples/', json=example_data,
                                      headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403


@pytest.mark.anyio
async def test_update_example(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
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
                                headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "id": last_example_id,
        "title": "Example 1",
        "age": 2,
        "price": 2,
        "description": "string 1",
        "category_id": 1
    }

    fail_response = await client.put(f'/examples/-1', json=example_data,
                                     headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')

    fail_response = await client.put(f'/examples/{last_example_id}', json=example_data,
                                     headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403


@pytest.mark.anyio
async def test_delete_example(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    examples = await ExampleModel.filter().all()
    last_example_id = examples[-1].id
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    response = await client.delete(f'/examples/{last_example_id}',
                                   headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": f"Example {last_example_id} deleted",
        "details": None
    }

    fail_response = await client.delete(f'/examples/-1',
                                        headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')
    fail_response = await client.delete('/examples/-1',
                                        headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403
