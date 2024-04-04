import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from main import app
from users.models import User


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
async def test_get_user(client: AsyncClient):
    user_2 = await User.get(id=2)
    response = await client.get('/users/2')
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "username": 'Riwick',
        "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z')
    }

    cached_response = await client.get('/users/2')
    assert cached_response.status_code == 200
    assert cached_response.json() == {
        "id": 2,
        "username": 'Riwick',
        "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z')
    }

    fail_response = await client.get('/users/-1')
    assert fail_response.status_code == 404


@pytest.mark.anyio
async def test_get_users(client: AsyncClient):
    user_2 = await User.get(id=2)
    user_1 = await User.get(id=1)
    response = await client.get('/users/')
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "username": "string",
            "date_joined": user_1.date_joined.isoformat().replace('+00:00', 'Z')
        },
        {
            "id": 2,
            "username": 'Riwick',
            "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z')
        }
    ]


@pytest.mark.anyio
async def test_filters(client: AsyncClient):
    user_1 = await User.get(id=1)
    filter_response = await client.get('/users/?offset=0&limit=10&order_by=id&username=string')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 1,
        "username": "string",
        "date_joined": user_1.date_joined.isoformat().replace('+00:00', 'Z')
    }]

    filter_response = await client.get('/users/?offset=0&limit=10&order_by=id&user_id=1')
    assert filter_response.status_code == 200
    assert filter_response.json() == [{
        "id": 1,
        "username": "string",
        "date_joined": user_1.date_joined.isoformat().replace('+00:00', 'Z')
    }]


@pytest.mark.anyio
async def test_ordering(client: AsyncClient):
    user_2 = await User.get(id=2)
    user_1 = await User.get(id=1)
    ordering_response = await client.get('/users/?offset=0&limit=10&order_by=-id')
    assert ordering_response.status_code == 200
    assert ordering_response.json() == [
        {
            "id": 2,
            "username": "Riwick",
            "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z')
        },
        {
            "id": 1,
            "username": "string",
            "date_joined": user_1.date_joined.isoformat().replace('+00:00', 'Z')
        }
    ]

    ordering_response = await client.get('/users/?offset=0&limit=10&order_by=username')
    assert ordering_response.status_code == 200
    assert ordering_response.json() == [
        {
            "id": 2,
            "username": "Riwick",
            "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z')
        },
        {
            "id": 1,
            "username": "string",
            "date_joined": user_1.date_joined.isoformat().replace('+00:00', 'Z')
        }
    ]


@pytest.mark.anyio
async def test_profile(client: AsyncClient):
    user_2 = await User.get(id=2)
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    response = await client.get('/users/me',
                                headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "username": "Riwick",
        "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z'),
        "is_active": True,
        "is_superuser": True,
        "email": user_2.email
    }

    not_auth_response = await client.get('/users/me')
    assert not_auth_response.status_code == 401

    cached_response = await client.get('/users/me',
                                       headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert cached_response.status_code == 200
    assert response.json() == {
        "id": 2,
        "username": "Riwick",
        "date_joined": user_2.date_joined.isoformat().replace('+00:00', 'Z'),
        "is_active": True,
        "is_superuser": True,
        "email": user_2.email
    }


@pytest.mark.anyio
async def test_register(client: AsyncClient):
    example_data = {
        "username": "string 123",
        "password": "string",
        "email": "user123@example.com"
    }
    response = await client.post('/users/register', json=example_data)
    assert response.status_code == 200
    users = await User.filter().all()
    last_user = users[-1]
    assert response.json() == {
        "id": last_user.id,
        "username": last_user.username,
        "date_joined": last_user.date_joined.isoformat().replace('+00:00', 'Z')
    }

    example_data = {
        "username": "Riwick",
        "password": "string",
        "email": "user2@example.com"
    }

    fail_response = await client.post('/users/register', json=example_data)
    assert fail_response.status_code == 422


@pytest.mark.anyio
async def test_bad_login(client: AsyncClient):
    invalid_username = await client.post('/users/login', json={
        "username": "Riwick1",
        "password": "string"
    })
    assert invalid_username.status_code == 404
    assert invalid_username.json() == {"detail": "User does not exists"}

    invalid_password = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string123"
    })
    assert invalid_password.status_code == 404
    assert invalid_password.json() == {"detail": "Incorrect username or password"}


@pytest.mark.anyio
async def test_update_user(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    example_data = {
        "username": "STRING"
    }
    users = await User.filter().all()
    last_user = users[-1]
    response = await client.put(f'/users/{last_user.id}', json=example_data,
                                headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "id": last_user.id,
        "username": "STRING",
        "date_joined": last_user.date_joined.isoformat().replace('+00:00', 'Z')
    }

    fail_response = await client.put('/users/-1', json=example_data,
                                     headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')

    fail_response = await client.put(f'/users/{last_user.id}', json=example_data,
                                     headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403


@pytest.mark.anyio
async def test_delete_user(client: AsyncClient):
    get_admin_jwt_token = await client.post('/users/login', json={
        "username": "Riwick",
        "password": "string"
    })
    users = await User.filter().all()
    last_user_id = users[-1].id
    assert get_admin_jwt_token.status_code == 200
    admin_jwt_token = get_admin_jwt_token.json().get('access_token')
    admin_jwt_type = get_admin_jwt_token.json().get('token_type')
    response = await client.delete(f'/users/{last_user_id}',
                                   headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": f"User {last_user_id} deleted",
        "details": None
    }

    fail_response = await client.delete(f'/users/-1',
                                        headers={'Authorization': f'{admin_jwt_type.capitalize()} {admin_jwt_token}'})
    assert fail_response.status_code == 404

    get_user_jwt_token = await client.post('/users/login', json={
        "username": "string",
        "password": "string"
    })
    assert get_user_jwt_token.status_code == 200
    user_jwt_token = get_user_jwt_token.json().get('access_token')
    user_jwt_type = get_user_jwt_token.json().get('token_type')
    fail_response = await client.delete('/users/-1',
                                        headers={'Authorization': f'{user_jwt_type.capitalize()} {user_jwt_token}'})
    assert fail_response.status_code == 403
