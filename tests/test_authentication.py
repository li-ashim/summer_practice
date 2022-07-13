import httpx
import pytest
from fastapi import status

from app.routers.authentication import authenticate
from tests.conftest import test_user_1, test_user_2

user: dict = {}


@pytest.mark.asyncio
async def test_register_user(test_client: httpx.AsyncClient):
    response = await test_client.post('/register', json=test_user_1)
    assert response.status_code == status.HTTP_201_CREATED

    response = await test_client.post('/register', json=test_user_1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_authenticate():
    assert await authenticate(test_user_1['email'], test_user_1['password'])
    assert await authenticate(test_user_1['email'], 'wrong_password') is None
    assert await authenticate(
        test_user_2['email'], test_user_2['password']
    ) is None


@pytest.mark.asyncio
async def test_create_token(test_client: httpx.AsyncClient):
    response = await test_client.post('/token', data={
        'username': test_user_1['email'],
        'password': test_user_1['password']
    })
    assert response.status_code == status.HTTP_200_OK

    response = await test_client.post('/token', data={
        'username': test_user_2['email'],
        'password': test_user_2['password']
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
