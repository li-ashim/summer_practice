import httpx
import pytest
from fastapi import status

from tests.conftest import (test_card, test_collection_1, test_collection_2,
                            test_user_1, test_user_2)

private_collection: dict = {}
public_collection: dict = {}
header_user1: dict = {}
header_user2: dict = {}


@pytest.mark.asyncio
async def test_save_collection(test_client: httpx.AsyncClient):
    await test_client.post('/register', json=test_user_1)
    token = (await test_client.post('/token', data={
        'username': test_user_1['email'],
        'password': test_user_1['password']
    })).json()
    header_user1['Authorization'] = (token['token_type']
                                     + ' ' + token['access_token'])

    await test_client.post('/register', json=test_user_2)
    token = (await test_client.post('/token', data={
        'username': test_user_2['email'],
        'password': test_user_2['password']
    })).json()
    header_user2['Authorization'] = (token['token_type']
                                     + ' ' + token['access_token'])

    response = await test_client.post(
        '/collections/',
        json=test_collection_1,
        headers=header_user1
    )
    assert response.status_code == status.HTTP_201_CREATED
    private_collection.update(response.json())

    response = await test_client.post(
        '/collections/',
        json=test_collection_2,
        headers=header_user1
    )
    assert response.status_code == status.HTTP_201_CREATED
    public_collection.update(response.json())


@pytest.mark.asyncio
async def test_get_private_collections(test_client: httpx.AsyncClient):
    response = await test_client.get(
        '/collections/private', headers=header_user1
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_public_collections(test_client: httpx.AsyncClient):
    response = await test_client.get('/collections/public')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_private_collection_by_id(test_client: httpx.AsyncClient):
    response = await test_client.get(
        f'/collections/private/{private_collection["id"]}',
        headers=header_user1
    )
    assert response.status_code == status.HTTP_200_OK

    response = await test_client.get(
        f'/collections/private/{private_collection["id"]}',
        headers=header_user2
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_public_collection_by_id(test_client: httpx.AsyncClient):
    response = await test_client.get(
        f'/collections/public/{public_collection["id"]}', headers=header_user1
    )
    assert response.status_code == status.HTTP_200_OK

    response = await test_client.get(
        f'/collections/public/{public_collection["id"]}'
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_collection(test_client: httpx.AsyncClient):
    new_description_data = {'description': 'new test description 1'}
    new_title_data = {'title': 'new test collection 1'}
    response = await test_client.put(
        f'/collections/{private_collection["id"]}',
        json=new_description_data,
        headers=header_user1
    )
    assert response.status_code == status.HTTP_200_OK

    response = await test_client.put(
        f'/collections/{private_collection["id"]}',
        json=new_title_data,
        headers=header_user1
    )
    assert response.status_code == status.HTTP_200_OK

    private_collection.update(response.json())


@pytest.mark.asyncio
async def test_delete_empty_collection(test_client: httpx.AsyncClient):
    response = await test_client.delete(
        f'/collections/{private_collection["id"]}', headers=header_user2
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await test_client.delete(
        f'/collections/{private_collection["id"]}', headers=header_user1
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_nonempty_collection(test_client: httpx.AsyncClient):
    response = await test_client.post(
        '/collections/',
        json=test_collection_1,
        headers=header_user1
    )
    private_collection.update(response.json())
    collection_for_card = {
        'id': private_collection['id'],
        'title': private_collection['title']
    }
    test_card[  # type: ignore
        'collections'
    ].append(collection_for_card)
    await test_client.post('/cards/', json=test_card, headers=header_user1)

    response = await test_client.delete(
        f'/collections/{private_collection["id"]}', headers=header_user1
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
