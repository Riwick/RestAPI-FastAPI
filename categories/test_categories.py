import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from categories.models import Category
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
async def test_get_category(client: AsyncClient):
    response = await client.get('/categories/1')
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "string"
    }

    cached_response = await client.get('/categories/1')
    assert cached_response.status_code == 200
    assert cached_response.json() == {
        "id": 1,
        "title": "string"
    }

    fail_response = await client.get('/categories/-1')
    assert fail_response.status_code == 404


@pytest.mark.anyio
async def test_get_categories(client: AsyncClient):
    response = await client.get('/categories/')
    assert response.status_code == 200
    assert response.json() == [{
            "id": 1,
            "title": "string"
        },
        {
            "id": 2,
            "title": "string 2"
        }
    ]


@pytest.mark.anyio
async def test_filters(client: AsyncClient):
    filter_response = await client.get('/categories/?offset=0&limit=10&order_by=id&title=string')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 1,
        "title": "string"
    }]

    filter_response = await client.get('/categories/?offset=0&limit=10&order_by=id&cat_id=2')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 2,
        "title": "string 2"
    }]


@pytest.mark.anyio
async def test_ordering(client: AsyncClient):
    ordering_response = await client.get('/categories/?offset=0&limit=10&order_by=-id')
    assert ordering_response.status_code == 200
    assert ordering_response.json() == [{
            "id": 2,
            "title": "string 2"
        },
        {
            "id": 1,
            "title": "string"
        }
    ]

    ordering_response = await client.get('/categories/?offset=0&limit=10&order_by=-title')
    assert ordering_response.status_code == 200
    assert ordering_response.json() == [{
            "id": 2,
            "title": "string 2"
        },
        {
            "id": 1,
            "title": "string"
        }
    ]


@pytest.mark.anyio
async def test_create_category(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    example_data = {
        "title": "string 3",
    }
    response = await client.post('/categories/', json=example_data,
                                 headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')
    fail_response = await client.post('/categories/', json=example_data,
                                      headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403


@pytest.mark.anyio
async def test_update_category(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    example_data = {
        "title": "STRING"
    }
    categories = await Category.filter().all()
    last_category_id = categories[-1].id
    response = await client.put(f'/categories/{last_category_id}', json=example_data,
                                headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "id": last_category_id,
        "title": "STRING",
    }

    fail_response = await client.put(f'/categories/-1', json=example_data,
                                     headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')

    fail_response = await client.put(f'/categories/{last_category_id}', json=example_data,
                                     headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403


@pytest.mark.anyio
async def test_delete_category(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    categories = await Category.filter().all()
    last_category_id = categories[-1].id
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    response = await client.delete(f'/categories/{last_category_id}',
                                   headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": f"Category {last_category_id} deleted",
        "details": None
    }

    fail_response = await client.delete(f'/categories/-1',
                                        headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')
    fail_response = await client.delete('/categories/-1',
                                        headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403
