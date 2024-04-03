import pytest

from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = 'postgres://postgres:postgres@localhost:10001/test_db'
    initializer(modules=['examples.models', 'categories.models', 'users.models'], db_url=db_url)
    request.addfinalizer(finalizer)
